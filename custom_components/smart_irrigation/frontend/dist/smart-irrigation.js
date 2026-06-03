!function(e){"use strict";var t=function(e,a){return t=Object.setPrototypeOf||{__proto__:[]}instanceof Array&&function(e,t){e.__proto__=t;}||function(e,t){for(var a in t)Object.prototype.hasOwnProperty.call(t,a)&&(e[a]=t[a]);},t(e,a);};function a(e,a){if("function"!=typeof a&&null!==a)throw new TypeError("Class extends value "+String(a)+" is not a constructor or null");function i(){this.constructor=e;}t(e,a),e.prototype=null===a?Object.create(a):(i.prototype=a.prototype,new i());}var i=function(){return i=Object.assign||function(e){for(var t,a=1,i=arguments.length;a<i;a++)for(var n in t=arguments[a])Object.prototype.hasOwnProperty.call(t,n)&&(e[n]=t[n]);return e;},i.apply(this,arguments);};function n(e,t,a,i){var n,s=arguments.length,r=s<3?t:null===i?i=Object.getOwnPropertyDescriptor(t,a):i;if("object"==typeof Reflect&&"function"==typeof Reflect.decorate)r=Reflect.decorate(e,t,a,i);else for(var o=e.length-1;o>=0;o--)(n=e[o])&&(r=(s<3?n(r):s>3?n(t,a,r):n(t,a))||r);return s>3&&r&&Object.defineProperty(t,a,r),r;}function s(e,t,a){if(a||2===arguments.length)for(var i,n=0,s=t.length;n<s;n++)!i&&n in t||(i||(i=Array.prototype.slice.call(t,0,n)),i[n]=t[n]);return e.concat(i||Array.prototype.slice.call(t));}"function"==typeof SuppressedError&&SuppressedError;/**
     * @license
     * Copyright 2019 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const r=window,o=r.ShadowRoot&&(void 0===r.ShadyCSS||r.ShadyCSS.nativeShadow)&&"adoptedStyleSheets"in Document.prototype&&"replace"in CSSStyleSheet.prototype,l=Symbol(),d=new WeakMap();class u{constructor(e,t,a){if(this._$cssResult$=!0,a!==l)throw Error("CSSResult is not constructable. Use `unsafeCSS` or `css` instead.");this.cssText=e,this.t=t;}get styleSheet(){let e=this.o;const t=this.t;if(o&&void 0===e){const a=void 0!==t&&1===t.length;a&&(e=d.get(t)),void 0===e&&((this.o=e=new CSSStyleSheet()).replaceSync(this.cssText),a&&d.set(t,e));}return e;}toString(){return this.cssText;}}const c=(e,...t)=>{const a=1===e.length?e[0]:t.reduce((t,a,i)=>t+(e=>{if(!0===e._$cssResult$)return e.cssText;if("number"==typeof e)return e;throw Error("Value passed to 'css' function must be a 'css' function result: "+e+". Use 'unsafeCSS' to pass non-literal values, but take care to ensure page security.");})(a)+e[i+1],e[0]);return new u(a,e,l);},p=o?e=>e:e=>e instanceof CSSStyleSheet?(e=>{let t="";for(const a of e.cssRules)t+=a.cssText;return(e=>new u("string"==typeof e?e:e+"",void 0,l))(t);})(e):e/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */;var h;const g=window,m=g.trustedTypes,v=m?m.emptyScript:"",f=g.reactiveElementPolyfillSupport,_={toAttribute(e,t){switch(t){case Boolean:e=e?v:null;break;case Object:case Array:e=null==e?e:JSON.stringify(e);}return e;},fromAttribute(e,t){let a=e;switch(t){case Boolean:a=null!==e;break;case Number:a=null===e?null:Number(e);break;case Object:case Array:try{a=JSON.parse(e);}catch(e){a=null;}}return a;}},b=(e,t)=>t!==e&&(t==t||e==e),y={attribute:!0,type:String,converter:_,reflect:!1,hasChanged:b},w="finalized";class k extends HTMLElement{constructor(){super(),this._$Ei=new Map(),this.isUpdatePending=!1,this.hasUpdated=!1,this._$El=null,this._$Eu();}static addInitializer(e){var t;this.finalize(),(null!==(t=this.h)&&void 0!==t?t:this.h=[]).push(e);}static get observedAttributes(){this.finalize();const e=[];return this.elementProperties.forEach((t,a)=>{const i=this._$Ep(a,t);void 0!==i&&(this._$Ev.set(i,a),e.push(i));}),e;}static createProperty(e,t=y){if(t.state&&(t.attribute=!1),this.finalize(),this.elementProperties.set(e,t),!t.noAccessor&&!this.prototype.hasOwnProperty(e)){const a="symbol"==typeof e?Symbol():"__"+e,i=this.getPropertyDescriptor(e,a,t);void 0!==i&&Object.defineProperty(this.prototype,e,i);}}static getPropertyDescriptor(e,t,a){return{get(){return this[t];},set(i){const n=this[e];this[t]=i,this.requestUpdate(e,n,a);},configurable:!0,enumerable:!0};}static getPropertyOptions(e){return this.elementProperties.get(e)||y;}static finalize(){if(this.hasOwnProperty(w))return!1;this[w]=!0;const e=Object.getPrototypeOf(this);if(e.finalize(),void 0!==e.h&&(this.h=[...e.h]),this.elementProperties=new Map(e.elementProperties),this._$Ev=new Map(),this.hasOwnProperty("properties")){const e=this.properties,t=[...Object.getOwnPropertyNames(e),...Object.getOwnPropertySymbols(e)];for(const a of t)this.createProperty(a,e[a]);}return this.elementStyles=this.finalizeStyles(this.styles),!0;}static finalizeStyles(e){const t=[];if(Array.isArray(e)){const a=new Set(e.flat(1/0).reverse());for(const e of a)t.unshift(p(e));}else void 0!==e&&t.push(p(e));return t;}static _$Ep(e,t){const a=t.attribute;return!1===a?void 0:"string"==typeof a?a:"string"==typeof e?e.toLowerCase():void 0;}_$Eu(){var e;this._$E_=new Promise(e=>this.enableUpdating=e),this._$AL=new Map(),this._$Eg(),this.requestUpdate(),null===(e=this.constructor.h)||void 0===e||e.forEach(e=>e(this));}addController(e){var t,a;(null!==(t=this._$ES)&&void 0!==t?t:this._$ES=[]).push(e),void 0!==this.renderRoot&&this.isConnected&&(null===(a=e.hostConnected)||void 0===a||a.call(e));}removeController(e){var t;null===(t=this._$ES)||void 0===t||t.splice(this._$ES.indexOf(e)>>>0,1);}_$Eg(){this.constructor.elementProperties.forEach((e,t)=>{this.hasOwnProperty(t)&&(this._$Ei.set(t,this[t]),delete this[t]);});}createRenderRoot(){var e;const t=null!==(e=this.shadowRoot)&&void 0!==e?e:this.attachShadow(this.constructor.shadowRootOptions);return((e,t)=>{o?e.adoptedStyleSheets=t.map(e=>e instanceof CSSStyleSheet?e:e.styleSheet):t.forEach(t=>{const a=document.createElement("style"),i=r.litNonce;void 0!==i&&a.setAttribute("nonce",i),a.textContent=t.cssText,e.appendChild(a);});})(t,this.constructor.elementStyles),t;}connectedCallback(){var e;void 0===this.renderRoot&&(this.renderRoot=this.createRenderRoot()),this.enableUpdating(!0),null===(e=this._$ES)||void 0===e||e.forEach(e=>{var t;return null===(t=e.hostConnected)||void 0===t?void 0:t.call(e);});}enableUpdating(e){}disconnectedCallback(){var e;null===(e=this._$ES)||void 0===e||e.forEach(e=>{var t;return null===(t=e.hostDisconnected)||void 0===t?void 0:t.call(e);});}attributeChangedCallback(e,t,a){this._$AK(e,a);}_$EO(e,t,a=y){var i;const n=this.constructor._$Ep(e,a);if(void 0!==n&&!0===a.reflect){const s=(void 0!==(null===(i=a.converter)||void 0===i?void 0:i.toAttribute)?a.converter:_).toAttribute(t,a.type);this._$El=e,null==s?this.removeAttribute(n):this.setAttribute(n,s),this._$El=null;}}_$AK(e,t){var a;const i=this.constructor,n=i._$Ev.get(e);if(void 0!==n&&this._$El!==n){const e=i.getPropertyOptions(n),s="function"==typeof e.converter?{fromAttribute:e.converter}:void 0!==(null===(a=e.converter)||void 0===a?void 0:a.fromAttribute)?e.converter:_;this._$El=n,this[n]=s.fromAttribute(t,e.type),this._$El=null;}}requestUpdate(e,t,a){let i=!0;void 0!==e&&(((a=a||this.constructor.getPropertyOptions(e)).hasChanged||b)(this[e],t)?(this._$AL.has(e)||this._$AL.set(e,t),!0===a.reflect&&this._$El!==e&&(void 0===this._$EC&&(this._$EC=new Map()),this._$EC.set(e,a))):i=!1),!this.isUpdatePending&&i&&(this._$E_=this._$Ej());}async _$Ej(){this.isUpdatePending=!0;try{await this._$E_;}catch(e){Promise.reject(e);}const e=this.scheduleUpdate();return null!=e&&(await e),!this.isUpdatePending;}scheduleUpdate(){return this.performUpdate();}performUpdate(){var e;if(!this.isUpdatePending)return;this.hasUpdated,this._$Ei&&(this._$Ei.forEach((e,t)=>this[t]=e),this._$Ei=void 0);let t=!1;const a=this._$AL;try{t=this.shouldUpdate(a),t?(this.willUpdate(a),null===(e=this._$ES)||void 0===e||e.forEach(e=>{var t;return null===(t=e.hostUpdate)||void 0===t?void 0:t.call(e);}),this.update(a)):this._$Ek();}catch(e){throw t=!1,this._$Ek(),e;}t&&this._$AE(a);}willUpdate(e){}_$AE(e){var t;null===(t=this._$ES)||void 0===t||t.forEach(e=>{var t;return null===(t=e.hostUpdated)||void 0===t?void 0:t.call(e);}),this.hasUpdated||(this.hasUpdated=!0,this.firstUpdated(e)),this.updated(e);}_$Ek(){this._$AL=new Map(),this.isUpdatePending=!1;}get updateComplete(){return this.getUpdateComplete();}getUpdateComplete(){return this._$E_;}shouldUpdate(e){return!0;}update(e){void 0!==this._$EC&&(this._$EC.forEach((e,t)=>this._$EO(t,this[t],e)),this._$EC=void 0),this._$Ek();}updated(e){}firstUpdated(e){}}/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var z;k[w]=!0,k.elementProperties=new Map(),k.elementStyles=[],k.shadowRootOptions={mode:"open"},null==f||f({ReactiveElement:k}),(null!==(h=g.reactiveElementVersions)&&void 0!==h?h:g.reactiveElementVersions=[]).push("1.6.3");const S=window,x=S.trustedTypes,$=x?x.createPolicy("lit-html",{createHTML:e=>e}):void 0,A="$lit$",M=`lit$${(Math.random()+"").slice(9)}$`,E="?"+M,T=`<${E}>`,D=document,j=()=>D.createComment(""),O=e=>null===e||"object"!=typeof e&&"function"!=typeof e,C=Array.isArray,P="[ \t\n\f\r]",N=/<(?:(!--|\/[^a-zA-Z])|(\/?[a-zA-Z][^>\s]*)|(\/?$))/g,H=/-->/g,I=/>/g,L=RegExp(`>|${P}(?:([^\\s"'>=/]+)(${P}*=${P}*(?:[^ \t\n\f\r"'\`<>=]|("|')|))|$)`,"g"),B=/'/g,U=/"/g,R=/^(?:script|style|textarea|title)$/i,W=(e=>(t,...a)=>({_$litType$:e,strings:t,values:a}))(1),F=Symbol.for("lit-noChange"),q=Symbol.for("lit-nothing"),V=new WeakMap(),Z=D.createTreeWalker(D,129,null,!1);function Y(e,t){if(!Array.isArray(e)||!e.hasOwnProperty("raw"))throw Error("invalid template strings array");return void 0!==$?$.createHTML(t):t;}const G=(e,t)=>{const a=e.length-1,i=[];let n,s=2===t?"<svg>":"",r=N;for(let t=0;t<a;t++){const a=e[t];let o,l,d=-1,u=0;for(;u<a.length&&(r.lastIndex=u,l=r.exec(a),null!==l);)u=r.lastIndex,r===N?"!--"===l[1]?r=H:void 0!==l[1]?r=I:void 0!==l[2]?(R.test(l[2])&&(n=RegExp("</"+l[2],"g")),r=L):void 0!==l[3]&&(r=L):r===L?">"===l[0]?(r=null!=n?n:N,d=-1):void 0===l[1]?d=-2:(d=r.lastIndex-l[2].length,o=l[1],r=void 0===l[3]?L:'"'===l[3]?U:B):r===U||r===B?r=L:r===H||r===I?r=N:(r=L,n=void 0);const c=r===L&&e[t+1].startsWith("/>")?" ":"";s+=r===N?a+T:d>=0?(i.push(o),a.slice(0,d)+A+a.slice(d)+M+c):a+M+(-2===d?(i.push(void 0),t):c);}return[Y(e,s+(e[a]||"<?>")+(2===t?"</svg>":"")),i];};class K{constructor({strings:e,_$litType$:t},a){let i;this.parts=[];let n=0,s=0;const r=e.length-1,o=this.parts,[l,d]=G(e,t);if(this.el=K.createElement(l,a),Z.currentNode=this.el.content,2===t){const e=this.el.content,t=e.firstChild;t.remove(),e.append(...t.childNodes);}for(;null!==(i=Z.nextNode())&&o.length<r;){if(1===i.nodeType){if(i.hasAttributes()){const e=[];for(const t of i.getAttributeNames())if(t.endsWith(A)||t.startsWith(M)){const a=d[s++];if(e.push(t),void 0!==a){const e=i.getAttribute(a.toLowerCase()+A).split(M),t=/([.?@])?(.*)/.exec(a);o.push({type:1,index:n,name:t[2],strings:e,ctor:"."===t[1]?te:"?"===t[1]?ie:"@"===t[1]?ne:ee});}else o.push({type:6,index:n});}for(const t of e)i.removeAttribute(t);}if(R.test(i.tagName)){const e=i.textContent.split(M),t=e.length-1;if(t>0){i.textContent=x?x.emptyScript:"";for(let a=0;a<t;a++)i.append(e[a],j()),Z.nextNode(),o.push({type:2,index:++n});i.append(e[t],j());}}}else if(8===i.nodeType)if(i.data===E)o.push({type:2,index:n});else{let e=-1;for(;-1!==(e=i.data.indexOf(M,e+1));)o.push({type:7,index:n}),e+=M.length-1;}n++;}}static createElement(e,t){const a=D.createElement("template");return a.innerHTML=e,a;}}function X(e,t,a=e,i){var n,s,r,o;if(t===F)return t;let l=void 0!==i?null===(n=a._$Co)||void 0===n?void 0:n[i]:a._$Cl;const d=O(t)?void 0:t._$litDirective$;return(null==l?void 0:l.constructor)!==d&&(null===(s=null==l?void 0:l._$AO)||void 0===s||s.call(l,!1),void 0===d?l=void 0:(l=new d(e),l._$AT(e,a,i)),void 0!==i?(null!==(r=(o=a)._$Co)&&void 0!==r?r:o._$Co=[])[i]=l:a._$Cl=l),void 0!==l&&(t=X(e,l._$AS(e,t.values),l,i)),t;}class J{constructor(e,t){this._$AV=[],this._$AN=void 0,this._$AD=e,this._$AM=t;}get parentNode(){return this._$AM.parentNode;}get _$AU(){return this._$AM._$AU;}u(e){var t;const{el:{content:a},parts:i}=this._$AD,n=(null!==(t=null==e?void 0:e.creationScope)&&void 0!==t?t:D).importNode(a,!0);Z.currentNode=n;let s=Z.nextNode(),r=0,o=0,l=i[0];for(;void 0!==l;){if(r===l.index){let t;2===l.type?t=new Q(s,s.nextSibling,this,e):1===l.type?t=new l.ctor(s,l.name,l.strings,this,e):6===l.type&&(t=new se(s,this,e)),this._$AV.push(t),l=i[++o];}r!==(null==l?void 0:l.index)&&(s=Z.nextNode(),r++);}return Z.currentNode=D,n;}v(e){let t=0;for(const a of this._$AV)void 0!==a&&(void 0!==a.strings?(a._$AI(e,a,t),t+=a.strings.length-2):a._$AI(e[t])),t++;}}class Q{constructor(e,t,a,i){var n;this.type=2,this._$AH=q,this._$AN=void 0,this._$AA=e,this._$AB=t,this._$AM=a,this.options=i,this._$Cp=null===(n=null==i?void 0:i.isConnected)||void 0===n||n;}get _$AU(){var e,t;return null!==(t=null===(e=this._$AM)||void 0===e?void 0:e._$AU)&&void 0!==t?t:this._$Cp;}get parentNode(){let e=this._$AA.parentNode;const t=this._$AM;return void 0!==t&&11===(null==e?void 0:e.nodeType)&&(e=t.parentNode),e;}get startNode(){return this._$AA;}get endNode(){return this._$AB;}_$AI(e,t=this){e=X(this,e,t),O(e)?e===q||null==e||""===e?(this._$AH!==q&&this._$AR(),this._$AH=q):e!==this._$AH&&e!==F&&this._(e):void 0!==e._$litType$?this.g(e):void 0!==e.nodeType?this.$(e):(e=>C(e)||"function"==typeof(null==e?void 0:e[Symbol.iterator]))(e)?this.T(e):this._(e);}k(e){return this._$AA.parentNode.insertBefore(e,this._$AB);}$(e){this._$AH!==e&&(this._$AR(),this._$AH=this.k(e));}_(e){this._$AH!==q&&O(this._$AH)?this._$AA.nextSibling.data=e:this.$(D.createTextNode(e)),this._$AH=e;}g(e){var t;const{values:a,_$litType$:i}=e,n="number"==typeof i?this._$AC(e):(void 0===i.el&&(i.el=K.createElement(Y(i.h,i.h[0]),this.options)),i);if((null===(t=this._$AH)||void 0===t?void 0:t._$AD)===n)this._$AH.v(a);else{const e=new J(n,this),t=e.u(this.options);e.v(a),this.$(t),this._$AH=e;}}_$AC(e){let t=V.get(e.strings);return void 0===t&&V.set(e.strings,t=new K(e)),t;}T(e){C(this._$AH)||(this._$AH=[],this._$AR());const t=this._$AH;let a,i=0;for(const n of e)i===t.length?t.push(a=new Q(this.k(j()),this.k(j()),this,this.options)):a=t[i],a._$AI(n),i++;i<t.length&&(this._$AR(a&&a._$AB.nextSibling,i),t.length=i);}_$AR(e=this._$AA.nextSibling,t){var a;for(null===(a=this._$AP)||void 0===a||a.call(this,!1,!0,t);e&&e!==this._$AB;){const t=e.nextSibling;e.remove(),e=t;}}setConnected(e){var t;void 0===this._$AM&&(this._$Cp=e,null===(t=this._$AP)||void 0===t||t.call(this,e));}}class ee{constructor(e,t,a,i,n){this.type=1,this._$AH=q,this._$AN=void 0,this.element=e,this.name=t,this._$AM=i,this.options=n,a.length>2||""!==a[0]||""!==a[1]?(this._$AH=Array(a.length-1).fill(new String()),this.strings=a):this._$AH=q;}get tagName(){return this.element.tagName;}get _$AU(){return this._$AM._$AU;}_$AI(e,t=this,a,i){const n=this.strings;let s=!1;if(void 0===n)e=X(this,e,t,0),s=!O(e)||e!==this._$AH&&e!==F,s&&(this._$AH=e);else{const i=e;let r,o;for(e=n[0],r=0;r<n.length-1;r++)o=X(this,i[a+r],t,r),o===F&&(o=this._$AH[r]),s||(s=!O(o)||o!==this._$AH[r]),o===q?e=q:e!==q&&(e+=(null!=o?o:"")+n[r+1]),this._$AH[r]=o;}s&&!i&&this.j(e);}j(e){e===q?this.element.removeAttribute(this.name):this.element.setAttribute(this.name,null!=e?e:"");}}class te extends ee{constructor(){super(...arguments),this.type=3;}j(e){this.element[this.name]=e===q?void 0:e;}}const ae=x?x.emptyScript:"";class ie extends ee{constructor(){super(...arguments),this.type=4;}j(e){e&&e!==q?this.element.setAttribute(this.name,ae):this.element.removeAttribute(this.name);}}class ne extends ee{constructor(e,t,a,i,n){super(e,t,a,i,n),this.type=5;}_$AI(e,t=this){var a;if((e=null!==(a=X(this,e,t,0))&&void 0!==a?a:q)===F)return;const i=this._$AH,n=e===q&&i!==q||e.capture!==i.capture||e.once!==i.once||e.passive!==i.passive,s=e!==q&&(i===q||n);n&&this.element.removeEventListener(this.name,this,i),s&&this.element.addEventListener(this.name,this,e),this._$AH=e;}handleEvent(e){var t,a;"function"==typeof this._$AH?this._$AH.call(null!==(a=null===(t=this.options)||void 0===t?void 0:t.host)&&void 0!==a?a:this.element,e):this._$AH.handleEvent(e);}}class se{constructor(e,t,a){this.element=e,this.type=6,this._$AN=void 0,this._$AM=t,this.options=a;}get _$AU(){return this._$AM._$AU;}_$AI(e){X(this,e);}}const re=S.litHtmlPolyfillSupport;null==re||re(K,Q),(null!==(z=S.litHtmlVersions)&&void 0!==z?z:S.litHtmlVersions=[]).push("2.8.0");/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var oe,le;class de extends k{constructor(){super(...arguments),this.renderOptions={host:this},this._$Do=void 0;}createRenderRoot(){var e,t;const a=super.createRenderRoot();return null!==(e=(t=this.renderOptions).renderBefore)&&void 0!==e||(t.renderBefore=a.firstChild),a;}update(e){const t=this.render();this.hasUpdated||(this.renderOptions.isConnected=this.isConnected),super.update(e),this._$Do=((e,t,a)=>{var i,n;const s=null!==(i=null==a?void 0:a.renderBefore)&&void 0!==i?i:t;let r=s._$litPart$;if(void 0===r){const e=null!==(n=null==a?void 0:a.renderBefore)&&void 0!==n?n:null;s._$litPart$=r=new Q(t.insertBefore(j(),e),e,void 0,null!=a?a:{});}return r._$AI(e),r;})(t,this.renderRoot,this.renderOptions);}connectedCallback(){var e;super.connectedCallback(),null===(e=this._$Do)||void 0===e||e.setConnected(!0);}disconnectedCallback(){var e;super.disconnectedCallback(),null===(e=this._$Do)||void 0===e||e.setConnected(!1);}render(){return F;}}de.finalized=!0,de._$litElement$=!0,null===(oe=globalThis.litElementHydrateSupport)||void 0===oe||oe.call(globalThis,{LitElement:de});const ue=globalThis.litElementPolyfillSupport;null==ue||ue({LitElement:de}),(null!==(le=globalThis.litElementVersions)&&void 0!==le?le:globalThis.litElementVersions=[]).push("3.3.3");/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const ce=e=>t=>"function"==typeof t?((e,t)=>(customElements.define(e,t),t))(e,t):((e,t)=>{const{kind:a,elements:i}=t;return{kind:a,elements:i,finisher(t){customElements.define(e,t);}};})(e,t)/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */,pe=(e,t)=>"method"===t.kind&&t.descriptor&&!("value"in t.descriptor)?{...t,finisher(a){a.createProperty(t.key,e);}}:{kind:"field",key:Symbol(),placement:"own",descriptor:{},originalKey:t.key,initializer(){"function"==typeof t.initializer&&(this[t.key]=t.initializer.call(this));},finisher(a){a.createProperty(t.key,e);}};function he(e){return(t,a)=>void 0!==a?((e,t,a)=>{t.constructor.createProperty(a,e);})(e,t,a):pe(e,t);/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */}function ge(e){return he({...e,state:!0});}/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     *//**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */function me(e,t){return(({finisher:e,descriptor:t})=>(a,i)=>{var n;if(void 0===i){const i=null!==(n=a.originalKey)&&void 0!==n?n:a.key,s=null!=t?{kind:"method",placement:"prototype",key:i,descriptor:t(a.key)}:{...a,key:i};return null!=e&&(s.finisher=function(t){e(t,i);}),s;}{const n=a.constructor;void 0!==t&&Object.defineProperty(a,i,t(i)),null==e||e(n,i);}})({descriptor:a=>{const i={get(){var t,a;return null!==(a=null===(t=this.renderRoot)||void 0===t?void 0:t.querySelector(e))&&void 0!==a?a:null;},enumerable:!0,configurable:!0};if(t){const t="symbol"==typeof a?Symbol():"__"+a;i.get=function(){var a,i;return void 0===this[t]&&(this[t]=null!==(i=null===(a=this.renderRoot)||void 0===a?void 0:a.querySelector(e))&&void 0!==i?i:null),this[t];};}return i;}});}/**
     * @license
     * Copyright 2021 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */var ve;null===(ve=window.HTMLSlotElement)||void 0===ve||ve.prototype.assignedElements;let fe=!1,_e=null;const be=async()=>{if(fe&&_e)return _e;if(customElements.get("ha-checkbox")&&customElements.get("ha-slider")&&customElements.get("ha-panel-config")&&customElements.get("ha-entity-picker"))return Promise.resolve();fe=!0,_e=async function(){try{await new Promise(e=>{"requestIdleCallback"in window?requestIdleCallback(()=>e()):setTimeout(()=>e(),0);}),await customElements.whenDefined("partial-panel-resolver");const e=document.createDocumentFragment(),t=document.createElement("partial-panel-resolver");e.appendChild(t),t.hass={panels:[{url_path:"tmp",component_name:"config"}]},await new Promise(e=>queueMicrotask(()=>e())),t._updateRoutes(),await t.routerOptions.routes.tmp.load(),await customElements.whenDefined("ha-panel-config"),await new Promise(e=>queueMicrotask(()=>e()));const a=document.createElement("ha-panel-config");e.appendChild(a),await a.routerOptions.routes.automation.load(),customElements.get("ha-entity-picker")||(await Promise.race([customElements.whenDefined("ha-entity-picker"),new Promise(e=>setTimeout(e,3e3))])),e.textContent="";}catch(e){console.error("Failed to load HA form elements:",e);}}();try{await _e;}finally{fe=!1,_e=null;}};var ye,we;!function(e){e.language="language",e.system="system",e.comma_decimal="comma_decimal",e.decimal_comma="decimal_comma",e.space_comma="space_comma",e.none="none";}(ye||(ye={})),function(e){e.language="language",e.system="system",e.am_pm="12",e.twenty_four="24";}(we||(we={}));var ke=function(e,t,a,i){i=i||{},a=null==a?{}:a;var n=new Event(t,{bubbles:void 0===i.bubbles||i.bubbles,cancelable:Boolean(i.cancelable),composed:void 0===i.composed||i.composed});return n.detail=a,e.dispatchEvent(n),n;};const ze=`v${"2026.06.08"}`,Se="smart_irrigation",xe="precipitation_threshold_mm",$e="Open Weather Map",Ae="Pirate Weather",Me="Open-Meteo",Ee="minutes",Te="hours",De="days",je="imperial",Oe="metric",Ce="Dewpoint",Pe="Evapotranspiration",Ne="Humidity",He="Precipitation",Ie="Current Precipitation",Le="Pressure",Be="Solar Radiation",Ue="Temperature",Re="Windspeed",We="weather_service",Fe="sensor",qe="static",Ve="pressure_type",Ze="absolute",Ye="relative",Ge="none",Ke="source",Xe="sensorentity",Je="static_value",Qe="unit",et="aggregate",tt=["average","first","last","maximum","median","minimum","riemannsum","sum","delta"],at="sq ft",it="l/minute",nt="gal/minute",st="mm/h",rt="in/h",ot="name",lt="size",dt="throughput",ut="state",ct="duration",pt="module",ht="bucket",gt="multiplier",mt="mapping",vt="lead_time",ft="maximum_duration",_t="maximum_bucket",bt="drainage_rate",yt="linked_entity",wt="bucket_threshold",kt="flow_sensor",zt="zone_sequencing",St="sequential",xt="parallel",$t="rotating",At="zone_sequencing_max_consecutive_duration",Mt="zone_sequencing_min_absorption_time",Et=1,Tt=2,Dt=3,jt=4,Ot=e=>(...t)=>({_$litDirective$:e,values:t});class Ct{constructor(e){}get _$AU(){return this._$AM._$AU;}_$AT(e,t,a){this._$Ct=e,this._$AM=t,this._$Ci=a;}_$AS(e,t){return this.update(e,t);}update(e,t){return this.render(...t);}}/**
     * @license
     * Copyright 2017 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */class Pt extends Ct{constructor(e){if(super(e),this.et=q,e.type!==Tt)throw Error(this.constructor.directiveName+"() can only be used in child bindings");}render(e){if(e===q||null==e)return this.ft=void 0,this.et=e;if(e===F)return e;if("string"!=typeof e)throw Error(this.constructor.directiveName+"() called with a non-string value");if(e===this.et)return this.ft;this.et=e;const t=[e];return t.raw=t,this.ft={_$litType$:this.constructor.resultType,strings:t,values:[]};}}Pt.directiveName="unsafeHTML",Pt.resultType=1;const Nt=Ot(Pt);var Ht={actions:{delete:"Lösche",edit:"Bearbeiten",save:"Speichern",cancel:"Abbrechen",confirm_delete:"Löschen bestätigen",confirm_delete_zone:"Möchtest du diese Zone wirklich löschen?"},labels:{module:"Modul",no:"Nein",select:"Wähle",yes:"Ja",enabled:"Aktiviert",disabled:"Deaktiviert",before:"vor",after:"nach",settings:"Einstellungen",bulk_actions:"Sammelaktionen"},attributes:{size:"Größe",throughput:"Durchfluss",state:"Zustand",bucket:"Eimer",last_updated:"zuletzt aktualisiert",last_calculated:"zuletzt berechnet",number_of_data_points:"Anzahl Datenpunkte"},loading:"Laden",saving:"Speichern",units:{seconds:"Sekunden"},"loading-messages":{configuration:"Konfiguration wird geladen...",modules:"Module werden geladen...",general:"Laden..."},"saving-messages":{adding:"Hinzufügen...",saving:"Speichern..."},errors:{load_failed:"Daten konnten nicht geladen werden",save_failed:"Änderungen konnten nicht gespeichert werden",delete_failed:"Löschen fehlgeschlagen",action_failed:"Aktion fehlgeschlagen"}},It={"default-zone":"Standard Zone","default-mapping":"Standard Sensorgruppe"},Lt={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Beachte: Diese Beschreibung nutzt '.' als Dezimalzeichen und zeigt gerundete Werte. Das Modul berechnete einen Evapotranspirationsmangel von","bucket-was":"Der alte Vorrat war","new-bucket-values-is":"Der neue Vorrat ist","old-bucket-variable":"alter_Vorrat",delta:"Veränderung","bucket-less-than-zero-irrigation-necessary":"Wenn der Vorrat < 0 ist, ist eine Bewässerung nötig.","steps-taken-to-calculate-duration":"Für eine exakte Berechnung der Dauer, wurden folgende Schritte durchgeführt","precipitation-rate-defined-as":"Der Niederschlag ist","duration-is-calculated-as":"Die Dauer ist",bucket:"Vorrat","precipitation-rate-variable":"Niederschlag","multiplier-is-applied":"Der Multiplikator wird angewendet. Der Multiplikator ist","duration-after-multiplier-is":"also ist die Dauer","maximum-duration-is-applied":"Die maximale Dauer wird angewendet. Diese ist","duration-after-maximum-duration-is":"also ist die Dauer","lead-time-is-applied":"Zuletzt wird die Vorlaufzeit angewendet. Die Vorlaufzeit ist","duration-after-lead-time-is":"also ist die Dauer","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Wenn der Vorrat >= 0 ist, ist keine Bewässerung nötig und die Dauer ist gleich","maximum-bucket-is":"Der maximale Vorrat ist","max-bucket-variable":"max_bucket",drainage:"Drainage","drainage-rate":"Drainagerate",hours:"Stunden","drainage-rate-is":"Drainagerate bei Sättigung (Eimer am Maximum) beträgt","current-drainage-is":"Aktuelle Drainage berechnet als","no-drainage":"Aktuelle Drainage ist 0, weil"}}},Bt={pyeto:{description:"Die Berechnung der Verunstungsrate basiert auf der FAO56-Formel aus der PyETO-Bibliothek"},static:{description:"Modul mit einer statisch konfigurierbaren Verdunstungsrate."},passthrough:{description:"Pass Through übernimmt den Evapotranspirationssensor und gibt seinen Wert zurück. Auf diese Weise werden alle Berechnungen der Verdunstung umgangen, außer der Anwendung von Aggregaten wie Summe, Durchschnitt etc)."}},Ut={general:{cards:{"automatic-duration-calculation":{header:"Automatische Berechnung der Bewässerungsdauer",description:"Die Berechnung berücksichtigt die bis zu diesem Zeitpunkt gesammelten Wetterdaten und aktualisiert den Vorrat für jede automatische Zone. Anschließend wird die Dauer basierend auf dem neuen Vorrat angepasst und die gesammelten Wetterdaten entfernt.",labels:{"auto-calc-enabled":"Automatische Berechnung der Dauer pro Zone","auto-calc-time":"Berechne um","calc-time":"Berechnen um"}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Hinweis: Die automatische Aktualisierung der Wetterdaten erfolgt bei oder nach der automatischen Berechnung der Bewässerungsdauer"},header:"Automatische Aktualisierung der Wetterdaten",description:"Die Wetterdaten werden automatisch gesammelt und gespeichert. Zur Berechnung der Zonen und Bewässerungsdauer sind Wetterdaten erforderlich.",labels:{"auto-update-enabled":"Automatisches Update der Wetterdaten","auto-update-delay":"Update Verzögerung","auto-update-interval":"Update der Sensordaten alle","auto-update-schedule":"Aktualisierungsplan","auto-update-time":"Aktualisieren um"},options:{days:"Tage",hours:"Stunden",minutes:"Minuten"}},"automatic-clear":{header:"Automatisches Löschen der Wetterdaten",description:"Gesammelte Wetterdaten zu einem bestimmten Zeitpunkt automatisch entfernen. Damit wird sicher gestellt, dass keine Wetterdaten von vergangenen Tagen übrig bleiben. Entferne die Wetterdaten nicht vor der Berechnung und verwende diese Option nur, wenn du erwartest, dass das automatische Update Wetterdaten erfasst hat, nachdem der Tag berechnet wurde. Idealerweise sollte dieser Schnitt so spät wie möglich Tag durchgeführt werden.",labels:{"automatic-clear-enabled":"Automatisches Löschen der Wetterdaten","automatic-clear-time":"Löschen der Wetterdaten um"}},continuousupdates:{header:"Kontinuierliche Sensoraktualisierungen (experimentell)",description:"Experimentelle Funktion für granularere Wetterdaten.",labels:{continuousupdates:"Kontinuierliche Aktualisierungen aktivieren",sensor_debounce:"Sensor-Entprellung","sensor-debounce":"Sensor-Entprellzeit (ms)"}}},description:"Diese Seite ist für allgemeine Einstellungen.",title:"Allgemein"},help:{title:"Hilfe",cards:{"how-to-get-help":{title:"Hilfe bekommen","first-read-the":"Lies zuerst im",wiki:"Dokumentation","if-you-still-need-help":"Benötigst du weiterhin Hilfe, wende dich an das","community-forum":"Community Forum","or-open-a":"oder eröffne einen","github-issue":"GitHub-Issue","english-only":"nur Englisch"}}},mappings:{cards:{"add-mapping":{actions:{add:"Hinzufügen"},header:"Sensorgruppe hinzufügen"},mapping:{aggregates:{average:"Durchschnitt",first:"Erster",last:"Letzter",maximum:"Maximum",median:"Median",minimum:"Minimum",sum:"Summe",riemannsum:"Riemann-Summe",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"Diese Sensorgruppe kann nicht entfernt werden, da sie von mindestens einer Zone verwendet wird.",invalid_source:"Ungültige Quelle",source_does_not_exist:"Quelle existiert nicht. Bitte gib eine gültige Quelle ein, z. B. 'sensor.mysensor'."},items:{dewpoint:"Taupunkt",evapotranspiration:"Verdunstung",humidity:"Feuchtigkeit","maximum temperature":"Maximum-Temperatur","minimum temperature":"Minimum-Temperatur",precipitation:"Gesamtniederschlag",pressure:"Luftdruck","solar radiation":"Sonnenstrahlung",temperature:"Temperatur",windspeed:"Windgeschwindigkeit","current precipitation":"Aktueller Niederschlag"},pressure_types:{absolute:"absolut",relative:"relativ"},"pressure-type":"Der Luftdruck ist","sensor-aggregate-of-sensor-values-to-calculate":"des Sensors für die Berechnung.","sensor-aggregate-use-the":"Nutze den/die/das","sensor-entity":"Sensor Entität",static_value:"Wert","input-units":"Sensor Werte in",source:"Quelle",sources:{none:"Keine",weather_service:"Wetterdienst",sensor:"Sensor",static:"Fester Wert"}}},description:"Füge eine oder mehrere Sensorgruppen hinzu, die Wetterdaten von Weather service, Sensoren oder einer Kombination daraus abrufen. Jede Sensorgruppe kann für eine oder mehrere Zonen verwendet werden",labels:{"mapping-name":"Name"},no_items:"Es ist noch keine Sensorgruppe angelegt.",title:"Sensorgruppen","weather-records":{title:"Wetterdaten",timestamp:"Zeit",temperature:"Temp.",humidity:"Feuchte",dewpoint:"Taupunkt",wind:"Wind",pressure:"Druck",precipitation:"Niederschlag","retrieval-time":"Abgerufen","no-data":"Keine Wetterdaten für diese Sensorgruppe verfügbar"}},modules:{cards:{"add-module":{actions:{add:"Hinzufügen"},header:"Modul hinzufügen"},module:{errors:{"cannot-delete-module-because-zones-use-it":"Dieses Modul kann nicht entfernt werden, da es von mindestens einer Zone verwendet wird."},labels:{configuration:"Konfiguration",required:"Feld ist erforderlich"},"translated-options":{DontEstimate:"Nicht berechnen",EstimateFromSunHours:"Basierend auf den Sonnenstunden",EstimateFromTemp:"Basierend auf der Temperatur",EstimateFromSunHoursAndTemperature:"Basierend auf dem Durchschnitt von Sonnenstunden und Temperatur"}}},description:"Füge ein oder mehrere Module hinzu. Module berechnen die Bewässerungsdauer. Jedes Modul hat seine eigene Konfiguration und kann zur Berechnung der Bewässerungsdauer für eine oder mehrere Zonen verwendet werden.",no_items:"Es ist noch kein Module angelegt.",title:"Module"},zones:{actions:{add:"Hinzufügen",calculate:"Bewässerungsdauer berechnen.",information:"Informationen",update:"Wetterdaten aktualisieren.","reset-bucket":"Vorrat zurücksetzen","view-weather-info":"Wetterdaten anzeigen","view-weather-info-message":"Wetterdaten verfügbar für","view-watering-calendar":"Bewässerungskalender",irrigate_all:"Alle Zonen jetzt ausführen"},cards:{"add-zone":{actions:{add:"Hinzufügen"},header:"Zone hinzufügen"},"zone-actions":{actions:{"calculate-all":"Alle Zonen berechnen","update-all":"Alle Zonen aktualisieren","reset-all-buckets":"Alle Vorräte zurücksetzen","clear-all-weatherdata":"Alle Wetterdaten löschen"},header:"Aktionen für alle Zonen"}},description:"Füge eine oder mehrere Zonen hinzu. Die Bewässerungsdauer wird pro Zone, abhängig von Größe, Durchsatz, Status, Modul und Sensorgruppe berechnet.",labels:{bucket:"Vorrat",duration:"Dauer","lead-time":"Vorlaufzeit",mapping:"Sensorgruppe","maximum-duration":"Maximale Dauer",multiplier:"Multiplikator",name:"Name",size:"Größe",state:"Berechnung",states:{automatic:"Automatisch",disabled:"Aus",manual:"Manuell"},throughput:"Durchfluss","maximum-bucket":"Maximaler Vorrat",last_calculated:"Zuletzt berechnet","data-last-updated":"Daten zuletzt aktualisiert","data-number-of-data-points":"Anzahl der Messungen",drainage_rate:"Drainagerate",linked_entity:"Verknüpfte Schalter/Ventil-Entität",linked_entity_placeholder:"z.B. switch.garten_ventil",irrigate_now:"Jetzt bewässern",bucket_threshold:"Mindestdefizit für Bewässerung",flow_sensor:"Durchflussmesser-Sensor (optional)",flow_sensor_placeholder:"z. B. sensor.zone_flow_rate"},no_items:"Es ist noch keine Zone vorhanden.",title:"Zonen",confirm_irrigate:{title:"Bewässerung starten?",body:"Dies öffnet jetzt die verknüpften Ventile und umgeht alle Ausschlussbedingungen (Regen, Temperatur, Mindestabstand zwischen Bewässerungen).",all_linked_zones:"Alle verknüpften Zonen",toast_started:"Bewässerung gestartet",toast_failed:"Bewässerung fehlgeschlagen"}},schedules:{title:"Zeitpläne",description:"Erstellen Sie wiederkehrende Zeitpläne für automatische Berechnung, Aktualisierung oder Bewässerung – ohne Automationen.",add:"Zeitplan hinzufügen",no_items:"Noch keine Zeitpläne konfiguriert. Klicken Sie auf 'Zeitplan hinzufügen'.",zones_all:"Alle Zonen",zones_specific:"Bestimmte Zonen",hours:"Stunden",minutes:"Min",types:{daily:"Täglich",weekly:"Wöchentlich",monthly:"Monatlich",interval:"Alle N Stunden",sunrise:"Sonnenaufgang",sunset:"Sonnenuntergang",solar_azimuth:"Sonnenazimut"},actions:{calculate:"Berechnen (Bewässerungsdauer aktualisieren)",update:"Aktualisieren (Wetterdaten sammeln)",irrigate:"Bewässern (Ventile direkt steuern)"},days:{monday:"Mo",tuesday:"Di",wednesday:"Mi",thursday:"Do",friday:"Fr",saturday:"Sa",sunday:"So"},fields:{name:"Name",type:"Zeitplantyp",enabled:"Aktiviert",time:"Uhrzeit (HH:MM)",days_of_week:"Wochentage",day_of_month:"Tag des Monats",interval_hours:"Intervall",action:"Aktion",zones:"Zonen",start_date:"Startdatum (optional)",end_date:"Enddatum (optional)",offset_minutes:"Versatz von Sonnenaufgang/-untergang",account_for_duration:"Früh starten, damit Bewässerung zur Zielzeit endet",azimuth_angle:"Sonnenazimutwinkel"},dialog:{add_title:"Zeitplan hinzufügen",edit_title:"Zeitplan bearbeiten"}},info:{title:"Info",description:"Nächste Bewässerung und Systemstatus anzeigen.","configuration-not-available":"Konfiguration nicht verfügbar.",cards:{"zone-bucket-values":{title:"Zoneneimerstand & Dauer",labels:{bucket:"Eimer",duration:"Dauer"},"no-zones":"Keine Zonen konfiguriert"},"next-irrigation":{title:"Nächste Bewässerung",labels:{"next-start":"Nächster Start",duration:"Dauer",zones:"Zonen"},"no-data":"Keine Daten verfügbar"},"irrigation-reason":{title:"Bewässerungsgrund",labels:{reason:"Grund",sunrise:"Sonnenaufgang","total-duration":"Gesamtdauer",explanation:"Erklärung"},"no-data":"Keine Daten verfügbar"},irrigate_now:{title:"Jetzt bewässern",description:"Bewässerung sofort für alle Zonen mit verknüpfter Entität starten. Übersprungbedingungen werden ignoriert.",button_all:"Alle Zonen jetzt starten",no_linked_zones:"Keine Zonen haben eine verknüpfte Schalter/Ventil-Entität mit berechneter Dauer."}}},setup:{title:"Einrichtung"}},Rt="Smart Irrigation",Wt={title:"Standortkoordinaten",description:"Konfigurieren Sie Standortkoordinaten für den Abruf von Wetterdaten. Sie können manuelle Koordinaten verwenden, die sich von Ihrem Home Assistant Standort unterscheiden.",manual_enabled:"Manuelle Koordinaten verwenden",use_ha_location:"Home Assistant Standort verwenden",latitude:"Breitengrad (Dezimalgrad)",longitude:"Längengrad (Dezimalgrad)",elevation:"Höhe (Meter über dem Meeresspiegel)",current_ha_coords:"Aktuelle Home Assistant Koordinaten"},Ft={title:"Tage zwischen Bewässerungen",description:"Konfigurieren Sie die Mindestanzahl an Tagen zwischen Bewässerungsereignissen.",label:"Minimale Tage zwischen Bewässerungen",help_text:"Auf 0 setzen zum Deaktivieren. Werte von 1–365 Tagen werden unterstützt."},qt={title:"Bewässerungsstart-Auslöser",description:"Konfiguriere, wann die Bewässerung auf Basis von Sonnenereignissen starten soll. Du kannst mehrere Auslöser für verschiedene Zeitpläne hinzufügen. Bei Sonnenaufgang-Auslösern wird mit einem Versatz von 0 automatisch die Gesamtdauer aller aktivierten Zonen verwendet.",add_trigger:"Auslöser hinzufügen",edit_trigger:"Auslöser bearbeiten",delete_trigger:"Auslöser löschen",trigger_types:{sunrise:"Sonnenaufgang",sunset:"Sonnenuntergang",solar_azimuth:"Sonnenazimut"},fields:{name:{name:"Auslösername",description:"Ein aussagekräftiger Name zur Identifizierung dieses Auslösers"},type:{name:"Auslösertyp",description:"Die Art des Sonnenereignisses, das den Auslöser auslöst"},enabled:{name:"Aktiviert",description:"Ob dieser Auslöser derzeit aktiv ist"},offset_minutes:{name:"Versatz (Minuten)",description:"Minuten vor (-) oder nach (+) dem Sonnenereignis. Verwende bei Sonnenaufgang-Auslösern 0 für eine automatische Zeitsteuerung auf Basis der gesamten Zonendauer."},azimuth_angle:{name:"Azimutwinkel (Grad)",description:"Sonnenazimutwinkel in Grad, wobei 0=Nord, 90=Ost, 180=Süd, 270=West"},account_for_duration:{name:"Dauer berücksichtigen",description:"Wenn aktiviert, startet die Bewässerung früh genug, um zum angegebenen Zeitpunkt fertig zu sein. Wenn deaktiviert, startet die Bewässerung genau zum angegebenen Zeitpunkt."}},dialog:{add_title:"Bewässerungsstart-Auslöser hinzufügen",edit_title:"Bewässerungsstart-Auslöser bearbeiten",cancel:"Abbrechen",save:"Speichern",delete:"Löschen"},no_triggers:"Keine Bewässerungsstart-Auslöser konfiguriert. Das System verwendet das Standardverhalten (Sonnenaufgang mit der Gesamtdauer aller Zonen). Füge Auslöser hinzu, um den Bewässerungsstart anzupassen.",offset_auto:"Automatisch (aus der Gesamtdauer aller Zonen berechnet)",confirm_delete:"Möchtest du den Auslöser '{name}' wirklich löschen?",validation:{name_required:"Auslösername ist erforderlich",azimuth_invalid:"Der Azimutwinkel muss eine gültige Zahl sein"},help:{sunrise_offset:"Für Sonnenaufgang-Auslöser: Verwende negative Werte, um vor Sonnenaufgang zu starten, positive, um danach zu starten. Setze auf 0, um automatisch früh genug zu starten, damit alle Zonen vor Sonnenaufgang fertig sind.",sunset_offset:"Für Sonnenuntergang-Auslöser: Verwende negative Werte, um vor Sonnenuntergang zu starten, positive, um nach Sonnenuntergang zu starten.",azimuth_explanation:"Der Sonnenazimut ist die Himmelsrichtung der Sonne. 0°=Nord, 90°=Ost, 180°=Süd, 270°=West. Du kannst einen beliebigen Winkelwert eingeben (z. B. 450° = 90°, -30° = 330°). Nutze dies, um die Bewässerung auszulösen, wenn die Sonne eine bestimmte Position erreicht.",multiple_triggers:"Du kannst mehrere Auslöser konfigurieren. Jeder aktivierte Auslöser plant den Bewässerungsstart unabhängig."}},Vt={title:"Übersprungbedingungen",description:"Bewässerung automatisch überspringen, wenn die Bedingungen ungünstig sind. Niederschlagsprüfung, Temperatur und Wind erfordern einen Wetterdienst.",threshold_label:"Niederschlagsschwelle",threshold_description:"Mindestmenge an prognostiziertem Niederschlag (in mm) für heute und morgen, um die Bewässerung zu überspringen.",temp_section_title:"Bei niedriger Temperatur überspringen",temp_threshold_label:"Überspringen wenn Temperatur unter",wind_section_title:"Bei hoher Windgeschwindigkeit überspringen",wind_threshold_label:"Überspringen wenn Windgeschwindigkeit über",rain_sensor_section_title:"Regenmelder-Bedingung",rain_sensor_label:"Regenmelder-Entität (optional)",rain_sensor_placeholder:"z.B. binary_sensor.regen"},Zt={title:"Zonenreihenfolge",description:"Wenn mehrere Zonen bewässert werden müssen, legen Sie fest, ob alle gleichzeitig oder nacheinander laufen. Im sequenziellen Modus wartet das System, bis jede Zone fertig ist, bevor die nächste beginnt.",parallel:"Parallel (alle Zonen gleichzeitig)",sequential:"Sequenziell (eine Zone nach der anderen)",rotating:"Rotierend (Zonen wechseln sich ab)",max_consecutive_duration_label:"Max. ununterbrochene Laufzeit pro Zone",max_consecutive_duration_unit:"Minuten",min_absorption_time_label:"Min. Aufnahmezeit zwischen den Durchgängen",min_absorption_time_unit:"Minuten (0 = deaktiviert)"},Yt={title:"Wetterdienst",description:"Konfiguriere, welcher Wetterdienst für ET-Berechnungen und Überspringbedingungen verwendet wird.",enabled_label:"Wetterdienst aktivieren",service_label:"Wetterdienst",api_key_label:"API-Schlüssel",api_key_placeholder:"Leer lassen, um den vorhandenen Schlüssel zu behalten",api_key_configured:"API-Schlüssel ist konfiguriert",api_key_not_configured:"Kein API-Schlüssel konfiguriert",api_key_help:"Ein API-Schlüssel von deinem gewählten Wetterdienstanbieter. Open-Meteo benötigt keinen Schlüssel. OpenWeatherMap und Pirate Weather bieten beide kostenlose Kontingente.",no_api_key_needed:"Open-Meteo ist ein kostenloser Dienst und benötigt keinen API-Schlüssel.",save_button:"Wettereinstellungen speichern",saved:"Wettereinstellungen gespeichert",openmeteo:"Open-Meteo (kostenlos, kein Schlüssel nötig)",test_button:"Verbindung testen",test_button_testing:"Wird getestet…",test_success:"✓ Verbindung erfolgreich",test_error_invalid_auth:"✗ Ungültiger API-Schlüssel — prüfe, ob er korrekt und aktiv ist",test_error_cannot_connect:"✗ Verbindung nicht möglich — prüfe deine Internetverbindung",test_error_no_service:"✗ Wähle zuerst einen Wetterdienst",test_error_unknown:"✗ Test fehlgeschlagen — unbekannter Fehler",owm:"OpenWeatherMap",pw:"Pirate Weather"},Gt={zone_size:"Die gesamte bewässerte Fläche dieser Zone. Wird zusammen mit dem Durchsatz verwendet, um zu berechnen, wie viel Wasser pro Durchgang ausgebracht wird.",zone_throughput:"Gesamtwasserdurchfluss deines Bewässerungssystems für diese Zone (Liter/Min im metrischen System, Gal/Min im imperialen System). Prüfe das Datenblatt deiner Sprinkler oder miss, wie lange das Füllen eines bekannten Behälters dauert.",zone_drainage_rate:"Wie schnell überschüssiges Wasser aus dem Boden abfließt, wenn der Eimer voll ist. Typisch: Rasen 50 mm/h, sandiger Boden 100+ mm/h, Lehm 10 mm/h.",zone_bucket:"Aktuelles Wasserdefizit (negativ) oder -überschuss (positiv) für diese Zone. Die Bewässerung wird ausgelöst, wenn der Eimer unter den Schwellenwert fällt.",zone_maximum_bucket:"Maximaler Feuchtigkeitsüberschuss, den die Zone aufnehmen kann. Wasser über diesem Wert wird als Abfluss behandelt. Typischer Wert: 50 mm.",zone_bucket_threshold:"Die Bewässerung wird ausgelöst, wenn der Eimer unter diesen Wert fällt. Muss 0 oder negativ sein. 0 bedeutet, immer dann zu bewässern, wenn ein Defizit besteht.",zone_multiplier:"Skalierungsfaktor, der auf die berechnete Dauer angewendet wird. Über 1,0 erhöht, unter 1,0 verringert. Nützlich zur Feinabstimmung, ohne physische Messwerte zu ändern.",zone_lead_time:"Zusätzliche Sekunden vor dem Start der Bewässerung. Nutze dies für das Aufwärmen der Pumpe oder den Druckaufbau im System.",zone_maximum_duration:"Harte Obergrenze für einen einzelnen Bewässerungsdurchgang in Sekunden. Verhindert unkontrolliertes Bewässern. Standard: 3600 s (1 Stunde).",zone_linked_entity:"Die HA-Schalter- oder Ventil-Entität, die den Wasserfluss für diese Zone steuert. Diese Entität wird eingeschaltet, wenn die Bewässerung läuft.",zone_flow_sensor:"Optionaler Sensor zur Messung der tatsächlichen Durchflussrate. Wird nur zur Anzeige verwendet — beeinflusst die Dauerberechnung nicht.",general_autoupdatedelay:"Sekunden, die nach dem HA-Start bis zum ersten Abruf der Wetterdaten gewartet wird. Ermöglicht es anderen Integrationen, sich zuerst zu initialisieren.",general_sensor_debounce:"Mindestabstand in Millisekunden zwischen Sensormesswerten, um Rauschen von sich schnell ändernden Sensoren herauszufiltern.",general_calctime:"Tageszeit, zu der die Bewässerungsdauern aus den gesammelten Wetterdaten neu berechnet werden. Format: HH:MM (24-Stunden).",general_cleardatatime:"Tageszeit, zu der alte Wetterdaten gelöscht werden. Muss später als die Berechnungszeit eingestellt sein.",general_days_between:"Mindestanzahl an Tagen zwischen Bewässerungsereignissen für dieselbe Zone. Auf 0 setzen, um zu deaktivieren (bewässern, sobald ein Defizit besteht).",general_autoupdateinterval:"Wie oft Wetterdaten gesammelt werden. Wähle einen Wert, der frische Daten gegen API-Ratenbegrenzungen abwägt.",general_precipitation_threshold:"Die Bewässerung wird übersprungen, wenn der vorhergesagte Niederschlag für heute/morgen diesen Wert überschreitet.",general_temp_threshold:"Die Bewässerung wird übersprungen, wenn die aktuelle Temperatur unter diesem Wert liegt (z. B. zur Vermeidung von Frostschäden).",general_wind_threshold:"Die Bewässerung wird übersprungen, wenn die Windgeschwindigkeit diesen Wert überschreitet (starker Wind verringert die Effizienz und verursacht Abdrift)."},Kt={title:"Einrichtungsassistent",open_button:"Einrichtungsassistent",close:"Schließen",next:"Weiter",back:"Zurück",finish:"Fertigstellen",skip_step:"Diesen Schritt überspringen",step_indicator:"Schritt {current} von {total}",setup_complete_banner:"Einrichtung nicht abgeschlossen. Starte den Assistenten, um zu beginnen.",open_wizard:"Assistent öffnen",steps:{welcome:{title:"Willkommen bei Smart Irrigation",intro:"Dieser Assistent führt dich durch die vier Schritte, die nötig sind, damit deine erste Zone automatisch bewässert.",step1_label:"Wetterdienst — woher die Wetterdaten kommen",step2_label:"Berechnungsmodul — wie die Bewässerungsdauer berechnet wird",step3_label:"Sensorgruppe — welche Datenquellen verwendet werden",step4_label:"Zone — deine erste Bewässerungszone",tip:"Du kannst jeden Schritt überspringen und ihn später über den Tab „Einrichtung“ konfigurieren."},weather:{title:"Wetterdienst",description:"Wähle, wie Wetterdaten bezogen werden. Open-Meteo ist kostenlos und benötigt keinen API-Schlüssel — für die meisten Nutzer die einfachste Wahl."},module:{title:"Berechnungsmodul",description:"Ein Modul berechnet anhand der Evapotranspiration (ET), wie lange bewässert wird. Das PyETO-Modul (FAO-56-Methode) wird für die meisten Nutzer empfohlen.",pick_label:"Modultyp auswählen",no_modules:"Keine Modultypen verfügbar."},mapping:{title:"Sensorgruppe",description:"Eine Sensorgruppe verknüpft jede Wettervariable mit einer Datenquelle. Lege die wichtigsten Variablen unten fest — einzelne Sensorzuordnungen kannst du später über den Tab „Einrichtung → Sensorgruppen“ verfeinern.",name_label:"Name der Sensorgruppe",source_label:"Datenquelle für",use_weather_service:"Wetterdienst",use_sensor:"Sensor",use_static:"Statischer Wert",use_none:"Keine / nicht verwendet"},zone:{title:"Erste Zone",description:"Eine Zone ist ein Bewässerungsbereich (z. B. Rasen, Beet). Lege die physischen Eigenschaften fest, damit das System die korrekte Bewässerungsdauer berechnen kann.",name_label:"Zonenname",size_label:"Fläche",throughput_label:"Sprinkler-Durchsatz",entity_label:"Verknüpfter Schalter oder Ventil",entity_placeholder:"z. B. switch.garden_valve",module_label:"Berechnungsmodul",mapping_label:"Sensorgruppe"},done:{title:"Einrichtung abgeschlossen!",description:"Deine erste Zone ist bereit. Smart Irrigation berechnet die Bewässerungsdauern nun automatisch auf Basis der Wetterdaten.",next_steps:"Was du als Nächstes tun kannst:",tip1:"Gehe zu „Zonen“, um die berechneten Dauern und Eimerwerte anzuzeigen.",tip2:"Füge über den Tab „Zonen“ weitere Zonen hinzu.",tip3:"Verfeinere alle Einstellungen über den Tab „Einrichtung“.",go_zones:"Zu „Zonen“",go_setup:"Zur Einrichtung"}}},Xt={common:Ht,defaults:It,module:Lt,calcmodules:Bt,panels:Ut,title:Rt,coordinate_config:Wt,days_between_irrigation:Ft,irrigation_start_triggers:qt,weather_skip:Vt,zone_sequencing:Zt,weather_service_config:Yt,field_help:Gt,wizard:Kt},Jt=Object.freeze({__proto__:null,common:Ht,defaults:It,module:Lt,calcmodules:Bt,panels:Ut,title:Rt,coordinate_config:Wt,days_between_irrigation:Ft,irrigation_start_triggers:qt,weather_skip:Vt,zone_sequencing:Zt,weather_service_config:Yt,field_help:Gt,wizard:Kt,default:Xt}),Qt={loading:"Loading",saving:"Saving",actions:{delete:"Delete",edit:"Edit",save:"Save",cancel:"Cancel",confirm_delete:"Confirm Delete",confirm_delete_zone:"Are you sure you want to delete this zone?"},labels:{module:"Module",no:"No",select:"Select",yes:"Yes",enabled:"Enabled",disabled:"Disabled",before:"before",after:"after",settings:"Settings",bulk_actions:"Bulk Actions"},units:{seconds:"seconds"},attributes:{size:"size",throughput:"throughput",state:"state",bucket:"bucket",last_updated:"last updated",last_calculated:"last calculated",number_of_data_points:"number of data points"},"loading-messages":{configuration:"Loading configuration...",modules:"Loading modules...",general:"Loading..."},"saving-messages":{adding:"Adding...",saving:"Saving..."},errors:{load_failed:"Couldn't load data",save_failed:"Couldn't save changes",delete_failed:"Couldn't delete",action_failed:"Action failed"}},ea={"default-zone":"Default zone","default-mapping":"Default sensor group"},ta={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Note: this explanation uses '.' as decimal separator, shows rounded and metric values. Module returned Evapotranspiration deficiency ( = et0 * hour_multiplier + precipitation) of","bucket-was":"Bucket was","new-bucket-values-is":"New bucket value is",bucket:"bucket","old-bucket-variable":"old_bucket","max-bucket-variable":"max_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Since bucket < 0, irrigation is necessary","steps-taken-to-calculate-duration":"To calculate the exact duration, the following steps were taken","precipitation-rate-defined-as":"The precipitation rate is defined as","duration-is-calculated-as":"The duration is calculated as",drainage:"drainage","drainage-rate":"drainage_rate",hours:"hours","precipitation-rate-variable":"precipitation_rate","multiplier-is-applied":"Now, the multiplier is applied. The multiplier is","duration-after-multiplier-is":"hence the duration is","maximum-duration-is-applied":"Then, the maximum duration is applied. The maximum duration is","duration-after-maximum-duration-is":"hence the duration is","lead-time-is-applied":"Finally, the lead time is applied. The lead time is","duration-after-lead-time-is":"hence the final duration is","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Since bucket >= 0, no irrigation is necessary and duration is set to","maximum-bucket-is":"Maximum bucket size is","drainage-rate-is":"Drainage rate when saturated (bucket at max) is","current-drainage-is":"Current drainage is calculated as","no-drainage":"Current drainage is 0 because"}}},aa={pyeto:{description:"Calculate duration based on the FAO56 calculation from the PyETO library"},static:{description:"'Dummy' module with a static configurable delta"},passthrough:{description:"Passthrough module that returns the value of an Evapotranspiration sensor as delta"}},ia={general:{cards:{"automatic-duration-calculation":{header:"Automatic duration calculation",description:"Calculation takes collected weather data up to that point and updates the bucket for each automatic zone. Then, the duration is adjusted based on the new bucket value and the collected weather data is removed.",labels:{"auto-calc-enabled":"Automatically calculate irrigation durations","calc-time":"Calculate at"}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Warning: weather data update time on or after calculation time"},header:"Automatic weather data update",description:"Collect and store weather data automatically. Weather data is required to calculate zone buckets and durations.",labels:{"auto-update-enabled":"Automatically update weather data","auto-update-schedule":"Update schedule","auto-update-time":"Update at","auto-update-interval":"Update sensor data every","auto-update-delay":"Update delay"},options:{minutes:"minutes",hours:"hours",days:"days"}},"automatic-clear":{header:"Automatic weather data pruning",description:"Automatically remove collected weather data at a configured time. Use this to make sure that there is no left over weather data from previous days. Don't remove the weather data before you calculate and only use this option if you expect the automatic update to collect weather data after you calculated for the day. Ideally, you want to prune as late in the day as possible.",labels:{"automatic-clear-enabled":"Automatically clear collected weather data","automatic-clear-time":"Clear weather data at"}},continuousupdates:{header:"Continuous updates for sensors (experimental)",description:"This experimental feature will continuously update the sensor data. This is useful for sensor groups that use sources that provide continuous data, such as weather stations. This feature cannot be used for sensor groups that at least partly rely on weather services as continous polling of APIs will incur costs. Keep in mind that this is experimental and may not work as expected. Use at your own risk.",labels:{continuousupdates:"Enable continuous updates",sensor_debounce:"Sensor debounce"}}},description:"This page provides global settings.",title:"General"},schedules:{title:"Schedules",description:"Create recurring schedules to automatically calculate, update, or irrigate your zones. No automations needed.",add:"Add Schedule",no_items:"No schedules configured yet. Click 'Add Schedule' to get started.",zones_all:"All zones",zones_specific:"Specific zones",hours:"hours",minutes:"min",types:{daily:"Daily",weekly:"Weekly",monthly:"Monthly",interval:"Every N hours",sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar azimuth"},actions:{calculate:"Calculate (update irrigation duration)",update:"Update (collect weather data)",irrigate:"Irrigate (run valves directly)"},days:{monday:"Mon",tuesday:"Tue",wednesday:"Wed",thursday:"Thu",friday:"Fri",saturday:"Sat",sunday:"Sun"},fields:{name:"Name",type:"Schedule type",enabled:"Enabled",time:"Time (HH:MM)",days_of_week:"Days of week",day_of_month:"Day of month",interval_hours:"Interval",action:"Action",zones:"Zones",start_date:"Start date (optional)",end_date:"End date (optional)",offset_minutes:"Offset from sunrise/sunset",account_for_duration:"Start early so irrigation finishes at trigger time",azimuth_angle:"Solar azimuth angle"},dialog:{add_title:"Add Schedule",edit_title:"Edit Schedule"}},setup:{title:"Setup"},help:{title:"Help",cards:{"how-to-get-help":{title:"How to get help","first-read-the":"First, read the",wiki:"Documentation","if-you-still-need-help":"If you still need help reach out on the","community-forum":"Community forum","or-open-a":"or open a","github-issue":"Github Issue","english-only":"English only"}}},info:{title:"Info",description:"View information about next irrigation and system status.","configuration-not-available":"Configuration not available.",cards:{"zone-bucket-values":{title:"Zone Bucket Values & Duration",labels:{bucket:"Bucket",duration:"Duration"},"no-zones":"No zones configured"},"next-irrigation":{title:"Next Irrigation",labels:{"next-start":"Next start",duration:"Duration",zones:"Zones"},"no-data":"No data available"},"irrigation-reason":{title:"Irrigation Reason",labels:{reason:"Reason",sunrise:"Sunrise","total-duration":"Total duration",explanation:"Explanation"},"no-data":"No data available"},irrigate_now:{title:"Irrigate Now",description:"Immediately start irrigation for all zones that have a linked entity. Skip conditions are ignored.",button_all:"Run all zones now",no_linked_zones:"No zones have a linked switch/valve entity with a calculated duration."}}},mappings:{cards:{"add-mapping":{actions:{add:"Add sensor group"},header:"Add sensor groups"},mapping:{aggregates:{average:"Average",first:"First",last:"Last",maximum:"Maximum",median:"Median",minimum:"Minimum",riemannsum:"Riemann sum",sum:"Sum",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"You cannot delete this sensor group because there is at least one zone using it.",invalid_source:"Invalid source",source_does_not_exist:"Source does not exist. Please enter a valid source, such as 'sensor.mysensor'."},items:{dewpoint:"Dewpoint",evapotranspiration:"Evapotranspiration",humidity:"Humidity","maximum temperature":"Maximum temperature","minimum temperature":"Minimum temperature",precipitation:"Total precipitation","current precipitation":"Current precipitation",pressure:"Pressure","solar radiation":"Solar radiation",temperature:"Temperature",windspeed:"Wind speed"},pressure_types:{absolute:"absolute",relative:"relative"},"pressure-type":"Pressure is","sensor-aggregate-of-sensor-values-to-calculate":"of sensor values to calculate duration","sensor-aggregate-use-the":"Use the","sensor-entity":"Sensor entity",static_value:"Value","input-units":"Input provides values in",source:"Source",sources:{none:"None",weather_service:"Weather service",sensor:"Sensor",static:"Static value"}}},description:"Add one or more sensor groups that retrieve weather data from Weather service, from sensors or a combination of these. You can map each sensor group to one or more zones",labels:{"mapping-name":"Name"},no_items:"There are no sensor group defined yet.",title:"Sensor Groups","weather-records":{title:"Weather Records",timestamp:"Time",temperature:"Temp",humidity:"Hum",dewpoint:"Dew",wind:"Wind",pressure:"Press",precipitation:"Precip","retrieval-time":"Retrieved","no-data":"No weather data available for this sensor group"}},modules:{cards:{"add-module":{actions:{add:"Add module"},header:"Add module"},module:{errors:{"cannot-delete-module-because-zones-use-it":"You cannot delete this module because there is at least one zone using it."},labels:{configuration:"Configuration",required:"indicates a required field"},"translated-options":{DontEstimate:"Do not estimate",EstimateFromSunHours:"Estimate from sun hours",EstimateFromTemp:"Estimate from temperature",EstimateFromSunHoursAndTemperature:"Estimate from average of sun hours and temperature"}}},description:"Add one or more modules that calculate irrigation duration. Each module comes with its own configuration and can be used to calculate duration for one or more zones.",no_items:"There are no modules defined yet.",title:"Modules"},zones:{actions:{add:"Add",calculate:"Calculate",information:"Information",update:"Update","reset-bucket":"Reset bucket","view-weather-info":"View weather data","view-weather-info-message":"Weather data available for","view-watering-calendar":"View watering calendar",irrigate_all:"Run All Zones Now"},cards:{"add-zone":{actions:{add:"Add zone"},header:"Add zone"},"zone-actions":{actions:{"calculate-all":"Calculate all zones","update-all":"Update all zones","reset-all-buckets":"Reset all buckets","clear-all-weatherdata":"Clear all weather data"},header:"Actions on all zones"}},description:"Specify one or more irrigation zones here. The irrigation duration is calculated per zone, depending on size, throughput, state, module and sensor group.",labels:{bucket:"Bucket",duration:"Duration","lead-time":"Lead time",mapping:"Sensor Group","maximum-duration":"Maximum duration",multiplier:"Multiplier",name:"Name",size:"Size",state:"State",states:{automatic:"Automatic",disabled:"Disabled",manual:"Manual"},throughput:"Throughput","maximum-bucket":"Maximum bucket",last_calculated:"Last calculated","data-last-updated":"Data last updated","data-number-of-data-points":"Number of data points",drainage_rate:"Drainage rate",linked_entity:"Linked switch/valve entity",linked_entity_placeholder:"e.g. switch.garden_valve",flow_sensor:"Flow meter sensor (optional)",flow_sensor_placeholder:"e.g. sensor.zone_flow_rate",irrigate_now:"Irrigate Now",bucket_threshold:"Minimum deficit to irrigate"},no_items:"There are no zones defined yet.",title:"Zones",confirm_irrigate:{title:"Start irrigation?",body:"This opens the linked valve(s) now and bypasses all skip conditions (rain, temperature, minimum days between watering).",all_linked_zones:"All linked zones",toast_started:"Irrigation started",toast_failed:"Irrigation failed"}}},na="Smart Irrigation",sa={title:"Weather Service",description:"Configure which weather service to use for ET calculations and skip conditions.",enabled_label:"Enable weather service",service_label:"Weather service",api_key_label:"API key",api_key_placeholder:"Leave blank to keep existing key",api_key_configured:"API key is configured",api_key_not_configured:"No API key configured",api_key_help:"An API key from your chosen weather service provider. Open-Meteo does not require a key. OpenWeatherMap and Pirate Weather both offer free tiers.",no_api_key_needed:"Open-Meteo is a free service and requires no API key.",save_button:"Save weather settings",saved:"Weather settings saved",owm:"OpenWeatherMap",pw:"Pirate Weather",openmeteo:"Open-Meteo (free, no key needed)",test_button:"Test Connection",test_button_testing:"Testing…",test_success:"✓ Connection successful",test_error_invalid_auth:"✗ Invalid API key — check that it is correct and active",test_error_cannot_connect:"✗ Cannot connect — check your internet connection",test_error_no_service:"✗ Select a weather service first",test_error_unknown:"✗ Test failed — unknown error"},ra={title:"Irrigation Start Triggers",description:"Configure when irrigation should start based on solar events. You can add multiple triggers for different schedules. For sunrise triggers, leaving offset at 0 will automatically use the total duration of all enabled zones.",add_trigger:"Add Trigger",edit_trigger:"Edit Trigger",delete_trigger:"Delete Trigger",trigger_types:{sunrise:"Sunrise",sunset:"Sunset",solar_azimuth:"Solar Azimuth"},fields:{name:{name:"Trigger Name",description:"A descriptive name to identify this trigger"},type:{name:"Trigger Type",description:"The type of solar event to trigger on"},enabled:{name:"Enabled",description:"Whether this trigger is currently active"},offset_minutes:{name:"Offset (minutes)",description:"Minutes before (-) or after (+) the solar event. For sunrise triggers, use 0 for automatic timing based on total zone duration."},azimuth_angle:{name:"Azimuth Angle (degrees)",description:"Solar azimuth angle in degrees where 0=North, 90=East, 180=South, 270=West"},account_for_duration:{name:"Account for Duration",description:"When enabled, irrigation will start early enough to finish at the specified time. When disabled, irrigation will start exactly at the specified time."}},dialog:{add_title:"Add Irrigation Start Trigger",edit_title:"Edit Irrigation Start Trigger",cancel:"Cancel",save:"Save",delete:"Delete"},no_triggers:"No irrigation start triggers configured. The system will use the default behavior (sunrise with total zone duration). Add triggers to customize when irrigation starts.",offset_auto:"Auto (calculated from total zone duration)",confirm_delete:"Are you sure you want to delete the trigger '{name}'?",validation:{name_required:"Trigger name is required",azimuth_invalid:"Azimuth angle must be a valid number"},help:{sunrise_offset:"For sunrise triggers: Use negative values to start before sunrise, positive to start after. Set to 0 to automatically start early enough to complete all zones before sunrise.",sunset_offset:"For sunset triggers: Use negative values to start before sunset, positive to start after sunset.",azimuth_explanation:"Solar azimuth is the compass direction of the sun. 0°=North, 90°=East, 180°=South, 270°=West. You can enter any angle value (e.g., 450° = 90°, -30° = 330°). Use this to trigger irrigation when the sun reaches a specific position.",multiple_triggers:"You can configure multiple triggers. Each enabled trigger will independently schedule irrigation starts."}},oa={title:"Skip Conditions",description:"Automatically skip irrigation when conditions are unfavorable. Precipitation check requires a weather service. Temperature and wind checks also require a weather service.",threshold_label:"Precipitation Threshold",threshold_description:"Minimum amount of precipitation (in mm) forecasted for today and tomorrow to skip irrigation.",temp_section_title:"Skip on low temperature",temp_threshold_label:"Skip if temperature is below",wind_section_title:"Skip on high wind speed",wind_threshold_label:"Skip if wind speed is above",rain_sensor_section_title:"Skip on rain sensor",rain_sensor_label:"Rain sensor entity (optional)",rain_sensor_placeholder:"e.g. binary_sensor.rain"},la={title:"Location Coordinates",description:"Configure location coordinates for weather data retrieval. You can use manual coordinates different from your Home Assistant location if needed.",manual_enabled:"Use manual coordinates",use_ha_location:"Use Home Assistant location",latitude:"Latitude (decimal degrees)",longitude:"Longitude (decimal degrees)",elevation:"Elevation (meters above sea level)",current_ha_coords:"Current Home Assistant coordinates"},da={title:"Days Between Irrigation",description:"Configure the minimum number of days that must pass between irrigation events. This helps control watering frequency for water conservation and plant health management.\n\nTypical real-world use cases:\n• Lawn care: 1-2 day intervals prevent overwatering\n• Drought restrictions: 6+ day intervals for weekly watering\n• Deep-rooted plants: 3-7 day intervals for less frequent watering\n• Water conservation: Customizable based on climate and soil conditions",label:"Minimum days between irrigation",help_text:"Set to 0 to disable this feature. Values from 1-365 days are supported. This setting works alongside existing precipitation forecasting logic."},ua={title:"Zone Sequencing",description:"When multiple zones need irrigation, choose whether they run at the same time or one after another. Sequential mode waits for each zone to finish before starting the next. Rotating mode cycles through zones, giving each one a limited consecutive run before moving to the next.",parallel:"Parallel (all zones at once)",sequential:"Sequential (one zone at a time)",rotating:"Rotating (zones take turns)",max_consecutive_duration_label:"Max consecutive run time per zone",max_consecutive_duration_unit:"minutes",min_absorption_time_label:"Min. absorption time between slots",min_absorption_time_unit:"minutes (0 = disabled)"},ca={zone_size:"The total irrigated area of this zone. Used with throughput to calculate how much water is applied per run.",zone_throughput:"Total water flow of your irrigation system for this zone (litres/min in metric, gal/min in imperial). Check your sprinkler datasheet or measure by timing how long it takes to fill a known container.",zone_drainage_rate:"How fast excess water drains from the soil when the bucket is full. Typical: lawn 50 mm/h, sandy soil 100+ mm/h, clay 10 mm/h.",zone_bucket:"Current water deficit (negative) or surplus (positive) for this zone. Irrigation triggers when bucket drops below the threshold.",zone_maximum_bucket:"Maximum moisture surplus the zone can hold. Water above this level is treated as runoff. Typical value: 50 mm.",zone_bucket_threshold:"Irrigation triggers when the bucket drops below this value. Must be 0 or negative. 0 means irrigate whenever there is any deficit.",zone_multiplier:"Scale factor applied to the calculated duration. Use above 1.0 to increase, below 1.0 to decrease. Useful for fine-tuning without changing physical measurements.",zone_lead_time:"Extra seconds added before irrigation starts. Use for pump warm-up or system pressurisation.",zone_maximum_duration:"Hard cap on any single irrigation run in seconds. Prevents runaway watering. Default: 3600 s (1 hour).",zone_linked_entity:"The HA switch or valve entity controlling water flow for this zone. This entity is turned on when irrigation runs.",zone_flow_sensor:"Optional sensor measuring actual water flow rate. Used for reporting only — does not affect duration calculations.",general_autoupdatedelay:"Seconds to wait after HA starts before the first weather data fetch. Allows other integrations to initialise first.",general_sensor_debounce:"Minimum gap in milliseconds between sensor readings to filter noise from rapidly changing sensors.",general_calctime:"Time of day when irrigation durations are recalculated from collected weather data. Format: HH:MM (24-hour).",general_cleardatatime:"Time of day when old weather data is purged. Must be set later than the calculation time.",general_days_between:"Minimum days between irrigation events for the same zone. Set to 0 to disable (irrigate whenever deficit exists).",general_autoupdateinterval:"How often weather data is collected. Choose a value that balances fresh data against API rate limits.",general_precipitation_threshold:"Irrigation is skipped if forecasted precipitation for today/tomorrow exceeds this amount.",general_temp_threshold:"Irrigation is skipped if the current temperature is below this value (e.g. to prevent frost damage).",general_wind_threshold:"Irrigation is skipped if wind speed exceeds this value (high winds reduce efficiency and cause drift)."},pa={title:"Setup Wizard",open_button:"Setup Wizard",close:"Close",next:"Next",back:"Back",finish:"Finish",skip_step:"Skip this step",step_indicator:"Step {current} of {total}",setup_complete_banner:"Setup not complete. Run the wizard to get started.",open_wizard:"Open Wizard",steps:{welcome:{title:"Welcome to Smart Irrigation",intro:"This wizard guides you through the four steps needed to get your first zone irrigating automatically.",step1_label:"Weather Service — where to get weather data",step2_label:"Calculation Module — how irrigation duration is computed",step3_label:"Sensor Group — which data sources to use",step4_label:"Zone — your first irrigation zone",tip:"You can skip any step and configure it later from the Setup tab."},weather:{title:"Weather Service",description:"Choose how to get weather data. Open-Meteo is free and requires no API key — it is the easiest choice for most users."},module:{title:"Calculation Module",description:"A module calculates how long to irrigate based on evapotranspiration (ET). The PyETO module (FAO-56 method) is recommended for most users.",pick_label:"Select module type",no_modules:"No module types available."},mapping:{title:"Sensor Group",description:"A sensor group links each weather variable to a data source. Set the key variables below — you can refine individual sensor mappings later from the Setup → Sensor Groups tab.",name_label:"Sensor group name",source_label:"Data source for",use_weather_service:"Weather service",use_sensor:"Sensor",use_static:"Static value",use_none:"None / not used"},zone:{title:"First Zone",description:"A zone is one irrigation area (e.g. lawn, garden bed). Set the physical properties so the system can calculate the correct irrigation duration.",name_label:"Zone name",size_label:"Area",throughput_label:"Sprinkler throughput",entity_label:"Linked switch or valve",entity_placeholder:"e.g. switch.garden_valve",module_label:"Calculation module",mapping_label:"Sensor group"},done:{title:"Setup Complete!",description:"Your first zone is ready. Smart Irrigation will now calculate irrigation durations automatically based on weather data.",next_steps:"What you can do next:",tip1:"Go to Zones to view calculated durations and bucket values.",tip2:"Add more zones from the Zones tab.",tip3:"Refine all settings from the Setup tab.",go_zones:"Go to Zones",go_setup:"Go to Setup"}}},ha={common:Qt,defaults:ea,module:ta,calcmodules:aa,panels:ia,title:na,weather_service_config:sa,irrigation_start_triggers:ra,weather_skip:oa,coordinate_config:la,days_between_irrigation:da,zone_sequencing:ua,field_help:ca,wizard:pa},ga=Object.freeze({__proto__:null,common:Qt,defaults:ea,module:ta,calcmodules:aa,panels:ia,title:na,weather_service_config:sa,irrigation_start_triggers:ra,weather_skip:oa,coordinate_config:la,days_between_irrigation:da,zone_sequencing:ua,field_help:ca,wizard:pa,default:ha}),ma={actions:{delete:"Eliminar",edit:"Editar",save:"Guardar",cancel:"Cancelar",confirm_delete:"Confirmar eliminación",confirm_delete_zone:"¿Seguro que quieres eliminar esta zona?"},labels:{module:"Módulo",no:"No",select:"Seleccionar",yes:"Sí",enabled:"Activado",disabled:"Desactivado",before:"antes",after:"después",settings:"Ajustes",bulk_actions:"Acciones masivas"},attributes:{size:"Tamaño",throughput:"Rendimiento",state:"Estado",bucket:"depósito",last_updated:"última actualización",last_calculated:"último cálculo",number_of_data_points:"número de puntos de datos"},loading:"Cargando",saving:"Guardando",units:{seconds:"segundos"},"loading-messages":{configuration:"Cargando configuración...",modules:"Cargando módulos...",general:"Cargando..."},"saving-messages":{adding:"Añadiendo...",saving:"Guardando..."},errors:{load_failed:"No se pudieron cargar los datos",save_failed:"No se pudieron guardar los cambios",delete_failed:"No se pudo eliminar",action_failed:"La acción falló"}},va={"default-zone":"Zona de riego predeterminada","default-mapping":"Grupo de sensores predeterminado"},fa={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Nota: esta explicación utiliza '.' como separador decimal y muestra valores redondeados. El módulo devuelve una deficiencia de evapotranspiración de","bucket-was":"El cubo era","new-bucket-values-is":"El nuevo valor del cubo es","old-bucket-variable":"old_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Dado que cubo < 0, el riego es necesario","steps-taken-to-calculate-duration":"Para calcular la duración exacta, se siguieron los siguientes pasos","precipitation-rate-defined-as":"La tasa de precipitación se define como","duration-is-calculated-as":"La duración se calcula como",bucket:"cubo","precipitation-rate-variable":"precipitation_rate","multiplier-is-applied":"A continuación, se aplica el multiplicador. El multiplicador es","duration-after-multiplier-is":"por lo que la duración es","maximum-duration-is-applied":"A continuación, se aplica la duración máxima. La duración máxima es","duration-after-maximum-duration-is":"por lo que la duración es","lead-time-is-applied":"Por último, se aplica el plazo de entrega. El plazo de entrega es","duration-after-lead-time-is":"por lo que la duración final es","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Como cubo >= 0, no es necesario regar y la duración se fija en","maximum-bucket-is":"El tamaño máximo de cubo es","max-bucket-variable":"max_bucket",drainage:"drenaje","drainage-rate":"tasa de drenaje",hours:"horas","drainage-rate-is":"La tasa de drenaje cuando está saturado (depósito al máximo) es","current-drainage-is":"El drenaje actual se calcula como","no-drainage":"El drenaje actual es 0 porque"}}},_a={pyeto:{description:"Calcular la duración a partir del cálculo FAO56 de la biblioteca PyETO"},static:{description:"Módulo 'de prueba' con un delta estático configurable"},passthrough:{description:"Módulo de paso que devuelve el valor de un sensor de evapotranspiración como delta"}},ba={general:{cards:{"automatic-duration-calculation":{header:"Cálculo automático de la duración",labels:{"auto-calc-enabled":"Cálculo automático de la duración de las zonas","auto-calc-time":"Calcular en","calc-time":"Calcular a las"},description:"El cálculo toma los datos meteorológicos recopilados hasta ese momento y actualiza el depósito de cada zona automática. Después, la duración se ajusta según el nuevo valor del depósito y se eliminan los datos meteorológicos recopilados."},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Advertencia: la hora de actualización de los datos meteorológicos es igual o posterior a la hora de cálculo"},header:"Actualización automática de los datos meteorológicos",labels:{"auto-update-enabled":"Actualizar automáticamente los datos meteorológicos","auto-update-first-update":"(Primer) Actualización a las","auto-update-interval":"Actualizar datos del sensor cada","auto-update-schedule":"Programa de actualización","auto-update-time":"Actualizar a las","auto-update-delay":"Retraso de actualización"},options:{days:"días",hours:"horas",minutes:"minutos"},description:"Recopila y almacena datos meteorológicos automáticamente. Los datos meteorológicos son necesarios para calcular los depósitos y las duraciones de las zonas."},"automatic-clear":{header:"Limpieza automática de datos meteorológicos",description:"Elimina automáticamente los datos meteorológicos recopilados a una hora configurada. Úsalo para asegurarte de que no queden datos meteorológicos de días anteriores. No elimines los datos meteorológicos antes de calcular y usa esta opción solo si esperas que la actualización automática recopile datos meteorológicos después de calcular para el día. Lo ideal es limpiar lo más tarde posible del día.",labels:{"automatic-clear-enabled":"Borrar automáticamente los datos meteorológicos recopilados","automatic-clear-time":"Borrar datos meteorológicos a las"}},continuousupdates:{header:"Actualizaciones continuas de sensores (experimental)",description:"Función experimental para datos meteorológicos más detallados.",labels:{continuousupdates:"Activar actualizaciones continuas",sensor_debounce:"Antirrebote del sensor","sensor-debounce":"Tiempo de antirrebote del sensor (ms)"}}},description:"Esta página provee configuraciones globales.",title:"General"},help:{title:"Ayuda",cards:{"how-to-get-help":{title:"Cómo obtener ayuda","first-read-the":"Primero lee la",wiki:"Documentación","if-you-still-need-help":"Si aún necesitas ayuda, puedes:","community-forum":"Comunidad/Foro","or-open-a":"o abrir un","github-issue":"Incidencia en GitHub","english-only":"sólo en inglés"}}},mappings:{cards:{"add-mapping":{actions:{add:"Añadir grupo de sensores"},header:"Añadir grupos de sensores"},mapping:{aggregates:{average:"Promedio",first:"Primero",last:"Último",maximum:"Máximo",median:"Mediana",minimum:"Mínimo",sum:"Suma",riemannsum:"Suma de Riemann",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"No puedes eliminar este grupo de sensores porque hay al menos una zona que lo está usando.",invalid_source:"Origen no válido",source_does_not_exist:"El origen no existe. Introduce un origen válido, como 'sensor.mysensor'."},items:{dewpoint:"Punto de rocío",evapotranspiration:"Evapotranspiración",humidity:"Humedad","maximum temperature":"Temperatura máxima","minimum temperature":"Temperatura mínima",precipitation:"Precipitación total",pressure:"Presión","solar radiation":"Radiación solar",temperature:"Temperatura",windspeed:"Velocidad del viento","current precipitation":"Precipitación actual"},"sensor-aggregate-of-sensor-values-to-calculate":"de los valores de los sensores para calcular la duración","sensor-aggregate-use-the":"Usar la","sensor-entity":"Entidad de sensor",static_value:"Valor estático","input-units":"Unidades de entrada",source:"Fuente",sources:{none:"Ninguno",weather_service:"Servicio meteorológico",sensor:"Sensor",static:"Valor estático"},pressure_types:{absolute:"absoluta",relative:"relativa"},"pressure-type":"La presión es"}},description:"Añada uno o más grupos de sensores que recuperen datos meteorológicos de Weather service, de sensores o de una combinación de éstos. Puede asignar cada grupo de sensores a una o más zonas",labels:{"mapping-name":"Nombre del grupo de sensores"},no_items:"Aún no hay grupos de sensores definidos.",title:"Grupos de sensores","weather-records":{title:"Registros meteorológicos",timestamp:"Hora",temperature:"Temp.",humidity:"Humidity",precipitation:"Precip.","retrieval-time":"Obtenido","no-data":"No hay datos meteorológicos disponibles para este grupo de sensores",dewpoint:"Rocío",wind:"Viento",pressure:"Presión"}},modules:{cards:{"add-module":{actions:{add:"Añadir módulo"},header:"Añadir módulo"},module:{errors:{"cannot-delete-module-because-zones-use-it":"No puedes eliminar este módulo porque hay al menos una zona que lo está usando."},labels:{configuration:"Configuración",required:"Requerido"},"translated-options":{DontEstimate:"No estimar",EstimateFromSunHours:"Estimar desde horas de sol",EstimateFromTemp:"Estimar desde temperatura",EstimateFromSunHoursAndTemperature:"Estimar a partir del promedio de horas de sol y temperatura"}}},description:"Añada uno o varios módulos que calculen la duración del riego. Cada módulo tiene su propia configuración y puede utilizarse para calcular la duración de una o varias zonas.",no_items:"Aún no hay módulos definidos.",title:"Módulos"},zones:{actions:{add:"Añadir",calculate:"Calcular",information:"Información",update:"Actualizar","reset-bucket":"Resetear cubo","view-weather-info":"Ver datos meteorológicos","view-weather-info-message":"Datos meteorológicos disponibles para","view-watering-calendar":"Calendario de riego",irrigate_all:"Ejecutar todas las zonas ahora"},cards:{"add-zone":{actions:{add:"Añadir zona"},header:"Añadir zona"},"zone-actions":{actions:{"calculate-all":"Calcular todas las zonas","update-all":"Actualizar todas las zonas","reset-all-buckets":"Resetear todos los cubos","clear-all-weatherdata":"Borrar todos los datos meteorológicos"},header:"Acciones en todas las zonas"}},description:"Especifique aquí una o varias zonas de riego. La duración del riego se calcula por zona, en función del tamaño, el rendimiento, el estado, el módulo y el grupo de sensores.",labels:{bucket:"Cubo",duration:"Duración","lead-time":"Tiempo de espera",mapping:"Grupo de sensores","maximum-duration":"Duración máxima",multiplier:"Multiplicador",name:"Nombre",size:"Tamaño",state:"Estado",states:{automatic:"Automático",disabled:"Desactivado",manual:"Manual"},throughput:"Rendimiento","maximum-bucket":"Cubo máximo",last_calculated:"Último cálculo","data-last-updated":"Datos actualizados por última vez","data-number-of-data-points":"Número de puntos de datos",drainage_rate:"Tasa de drenaje",linked_entity:"Entidad de interruptor/válvula vinculada",linked_entity_placeholder:"p.ej. switch.valvula_jardin",irrigate_now:"Regar ahora",bucket_threshold:"Déficit mínimo para regar",flow_sensor:"Sensor de caudalímetro (opcional)",flow_sensor_placeholder:"p. ej. sensor.zone_flow_rate"},no_items:"Aún no hay zonas definidas.",title:"Zonas",confirm_irrigate:{title:"¿Iniciar el riego?",body:"Esto abrirá ahora las válvulas vinculadas e ignora todas las condiciones de exclusión (lluvia, temperatura, días mínimos entre riegos).",all_linked_zones:"Todas las zonas vinculadas",toast_started:"Riego iniciado",toast_failed:"Error en el riego"}},schedules:{title:"Programas",description:"Cree programas recurrentes para calcular, actualizar o regar automáticamente — sin automatizaciones.",add:"Añadir programa",no_items:"Aún no hay programas configurados. Haga clic en 'Añadir programa'.",zones_all:"Todas las zonas",zones_specific:"Zonas específicas",hours:"horas",minutes:"min",types:{daily:"Diario",weekly:"Semanal",monthly:"Mensual",interval:"Cada N horas",sunrise:"Amanecer",sunset:"Atardecer",solar_azimuth:"Azimut solar"},actions:{calculate:"Calcular (actualizar duración de riego)",update:"Actualizar (recopilar datos meteorológicos)",irrigate:"Regar (controlar válvulas directamente)"},days:{monday:"Lu",tuesday:"Ma",wednesday:"Mi",thursday:"Ju",friday:"Vi",saturday:"Sá",sunday:"Do"},fields:{name:"Nombre",type:"Tipo de programa",enabled:"Activado",time:"Hora (HH:MM)",days_of_week:"Días de la semana",day_of_month:"Día del mes",interval_hours:"Intervalo",action:"Acción",zones:"Zonas",start_date:"Fecha de inicio (opcional)",end_date:"Fecha de fin (opcional)",offset_minutes:"Desplazamiento desde amanecer/atardecer",account_for_duration:"Iniciar antes para que el riego termine a la hora objetivo",azimuth_angle:"Ángulo de azimut solar"},dialog:{add_title:"Añadir programa",edit_title:"Editar programa"}},info:{title:"Información",description:"Ver información sobre el próximo riego y el estado del sistema.","configuration-not-available":"Configuración no disponible.",cards:{"zone-bucket-values":{title:"Valores de depósito y duración",labels:{bucket:"Depósito",duration:"Duración"},"no-zones":"No hay zonas configuradas"},"next-irrigation":{title:"Próximo riego",labels:{"next-start":"Próximo inicio",duration:"Duración",zones:"Zonas"},"no-data":"No hay datos disponibles"},"irrigation-reason":{title:"Motivo del riego",labels:{reason:"Razón",sunrise:"Amanecer","total-duration":"Duración total",explanation:"Explicación"},"no-data":"No hay datos disponibles"},irrigate_now:{title:"Regar ahora",description:"Iniciar riego inmediatamente para todas las zonas con entidad vinculada. Las condiciones de omisión se ignoran.",button_all:"Iniciar todas las zonas ahora",no_linked_zones:"Ninguna zona tiene una entidad de interruptor/válvula vinculada con duración calculada."}}},setup:{title:"Configuración"}},ya="Smart Irrigation",wa={title:"Coordenadas de Ubicación",description:"Configure las coordenadas de ubicación para obtener datos meteorológicos. Puede usar coordenadas manuales diferentes a la ubicación de Home Assistant si es necesario.",manual_enabled:"Usar coordenadas manuales",use_ha_location:"Usar ubicación de Home Assistant",latitude:"Latitud (grados decimales)",longitude:"Longitud (grados decimales)",elevation:"Elevación (metros sobre el nivel del mar)",current_ha_coords:"Coordenadas actuales de Home Assistant"},ka={title:"Días entre riegos",description:"Configure el número mínimo de días entre eventos de riego.",label:"Días mínimos entre riegos",help_text:"Establezca 0 para desactivar. Se admiten valores de 1 a 365 días."},za={title:"Disparadores de inicio de riego",description:"Configura cuándo debe iniciarse el riego según eventos solares. Puedes añadir varios disparadores para diferentes horarios. Para los disparadores de amanecer, dejar el desfase en 0 usará automáticamente la duración total de todas las zonas activadas.",add_trigger:"Añadir disparador",edit_trigger:"Editar disparador",delete_trigger:"Eliminar disparador",trigger_types:{sunrise:"Amanecer",sunset:"Atardecer",solar_azimuth:"Acimut solar"},fields:{name:{name:"Nombre del disparador",description:"Un nombre descriptivo para identificar este disparador"},type:{name:"Tipo de disparador",description:"El tipo de evento solar con el que activar"},enabled:{name:"Activado",description:"Si este disparador está actualmente activo"},offset_minutes:{name:"Desfase (minutos)",description:"Minutos antes (-) o después (+) del evento solar. Para los disparadores de amanecer, usa 0 para una temporización automática basada en la duración total de las zonas."},azimuth_angle:{name:"Ángulo de acimut (grados)",description:"Ángulo de acimut solar en grados donde 0=Norte, 90=Este, 180=Sur, 270=Oeste"},account_for_duration:{name:"Tener en cuenta la duración",description:"Si está activado, el riego comenzará con suficiente antelación para terminar a la hora indicada. Si está desactivado, el riego comenzará exactamente a la hora indicada."}},dialog:{add_title:"Añadir disparador de inicio de riego",edit_title:"Editar disparador de inicio de riego",cancel:"Cancelar",save:"Guardar",delete:"Eliminar"},no_triggers:"No hay disparadores de inicio de riego configurados. El sistema usará el comportamiento predeterminado (amanecer con la duración total de las zonas). Añade disparadores para personalizar cuándo comienza el riego.",offset_auto:"Automático (calculado a partir de la duración total de las zonas)",confirm_delete:"¿Seguro que quieres eliminar el disparador '{name}'?",validation:{name_required:"El nombre del disparador es obligatorio",azimuth_invalid:"El ángulo de acimut debe ser un número válido"},help:{sunrise_offset:"Para los disparadores de amanecer: usa valores negativos para empezar antes del amanecer, positivos para empezar después. Pon 0 para empezar automáticamente con tiempo suficiente para completar todas las zonas antes del amanecer.",sunset_offset:"Para los disparadores de atardecer: usa valores negativos para empezar antes del atardecer, positivos para empezar después del atardecer.",azimuth_explanation:"El acimut solar es la dirección de la brújula del sol. 0°=Norte, 90°=Este, 180°=Sur, 270°=Oeste. Puedes introducir cualquier valor de ángulo (p. ej., 450° = 90°, -30° = 330°). Úsalo para activar el riego cuando el sol alcance una posición concreta.",multiple_triggers:"Puedes configurar varios disparadores. Cada disparador activado programará los inicios de riego de forma independiente."}},Sa={title:"Condiciones de omisión",description:"Omitir automáticamente el riego cuando las condiciones sean desfavorables. Las comprobaciones de precipitación, temperatura y viento requieren un servicio meteorológico.",threshold_label:"Umbral de precipitación",threshold_description:"Cantidad mínima de precipitación pronosticada (en mm) para hoy y mañana para omitir el riego.",temp_section_title:"Omitir por temperatura baja",temp_threshold_label:"Omitir si temperatura por debajo de",wind_section_title:"Omitir por viento fuerte",wind_threshold_label:"Omitir si velocidad del viento superior a",rain_sensor_section_title:"Condición del sensor de lluvia",rain_sensor_label:"Entidad del sensor de lluvia (opcional)",rain_sensor_placeholder:"p.ej. binary_sensor.lluvia"},xa={title:"Secuencia de zonas",description:"Cuando varias zonas necesitan riego, elija si se ejecutan al mismo tiempo o una tras otra. En modo secuencial, el sistema espera a que cada zona termine antes de iniciar la siguiente.",parallel:"Paralelo (todas las zonas a la vez)",sequential:"Secuencial (una zona a la vez)",rotating:"Rotativo (las zonas se turnan)",max_consecutive_duration_label:"Tiempo máx. de ejecución consecutiva por zona",max_consecutive_duration_unit:"minutos",min_absorption_time_label:"Tiempo mín. de absorción entre turnos",min_absorption_time_unit:"minutos (0 = desactivado)"},$a={title:"Servicio meteorológico",description:"Configura qué servicio meteorológico usar para los cálculos de ET y las condiciones de omisión.",enabled_label:"Activar servicio meteorológico",service_label:"Servicio meteorológico",api_key_label:"Clave API",api_key_placeholder:"Déjalo en blanco para conservar la clave existente",api_key_configured:"La clave API está configurada",api_key_not_configured:"No hay clave API configurada",api_key_help:"Una clave API de tu proveedor de servicio meteorológico elegido. Open-Meteo no requiere clave. OpenWeatherMap y Pirate Weather ofrecen niveles gratuitos.",no_api_key_needed:"Open-Meteo es un servicio gratuito y no requiere clave API.",save_button:"Guardar ajustes meteorológicos",saved:"Ajustes meteorológicos guardados",openmeteo:"Open-Meteo (gratis, sin clave)",test_button:"Probar conexión",test_button_testing:"Probando…",test_success:"✓ Conexión correcta",test_error_invalid_auth:"✗ Clave API no válida — comprueba que sea correcta y esté activa",test_error_cannot_connect:"✗ No se puede conectar — comprueba tu conexión a internet",test_error_no_service:"✗ Selecciona primero un servicio meteorológico",test_error_unknown:"✗ Prueba fallida — error desconocido",owm:"OpenWeatherMap",pw:"Pirate Weather"},Aa={zone_size:"La superficie total regada de esta zona. Se usa junto con el caudal para calcular cuánta agua se aplica por ciclo.",zone_throughput:"Flujo total de agua de tu sistema de riego para esta zona (litros/min en métrico, gal/min en imperial). Consulta la ficha técnica de tus aspersores o mídelo cronometrando cuánto tarda en llenarse un recipiente conocido.",zone_drainage_rate:"La rapidez con que el agua sobrante drena del suelo cuando el depósito está lleno. Típico: césped 50 mm/h, suelo arenoso 100+ mm/h, arcilla 10 mm/h.",zone_bucket:"Déficit (negativo) o superávit (positivo) de agua actual de esta zona. El riego se activa cuando el depósito cae por debajo del umbral.",zone_maximum_bucket:"Superávit máximo de humedad que la zona puede retener. El agua por encima de este nivel se trata como escorrentía. Valor típico: 50 mm.",zone_bucket_threshold:"El riego se activa cuando el depósito cae por debajo de este valor. Debe ser 0 o negativo. 0 significa regar siempre que haya déficit.",zone_multiplier:"Factor de escala aplicado a la duración calculada. Por encima de 1,0 aumenta, por debajo de 1,0 disminuye. Útil para ajustar sin cambiar las mediciones físicas.",zone_lead_time:"Segundos adicionales antes de que comience el riego. Úsalo para el calentamiento de la bomba o la presurización del sistema.",zone_maximum_duration:"Límite máximo absoluto para cualquier ciclo de riego individual en segundos. Evita el riego descontrolado. Predeterminado: 3600 s (1 hora).",zone_linked_entity:"La entidad de interruptor o válvula de HA que controla el flujo de agua de esta zona. Esta entidad se activa cuando se ejecuta el riego.",zone_flow_sensor:"Sensor opcional que mide el caudal real. Se usa solo para informes — no afecta a los cálculos de duración.",general_autoupdatedelay:"Segundos a esperar tras iniciar HA antes de la primera obtención de datos meteorológicos. Permite que otras integraciones se inicialicen primero.",general_sensor_debounce:"Intervalo mínimo en milisegundos entre lecturas del sensor para filtrar el ruido de sensores que cambian rápidamente.",general_calctime:"Hora del día en que se recalculan las duraciones de riego a partir de los datos meteorológicos recopilados. Formato: HH:MM (24 horas).",general_cleardatatime:"Hora del día en que se purgan los datos meteorológicos antiguos. Debe ser posterior a la hora de cálculo.",general_days_between:"Días mínimos entre eventos de riego para la misma zona. Pon 0 para desactivar (regar siempre que haya déficit).",general_autoupdateinterval:"Con qué frecuencia se recopilan los datos meteorológicos. Elige un valor que equilibre datos frescos con los límites de la API.",general_precipitation_threshold:"El riego se omite si la precipitación prevista para hoy/mañana supera esta cantidad.",general_temp_threshold:"El riego se omite si la temperatura actual es inferior a este valor (p. ej. para evitar daños por heladas).",general_wind_threshold:"El riego se omite si la velocidad del viento supera este valor (el viento fuerte reduce la eficiencia y causa deriva)."},Ma={title:"Asistente de configuración",open_button:"Asistente de configuración",close:"Cerrar",next:"Siguiente",back:"Atrás",finish:"Finalizar",skip_step:"Omitir este paso",step_indicator:"Paso {current} de {total}",setup_complete_banner:"Configuración incompleta. Ejecuta el asistente para empezar.",open_wizard:"Abrir asistente",steps:{welcome:{title:"Bienvenido a Smart Irrigation",intro:"Este asistente te guía por los cuatro pasos necesarios para que tu primera zona riegue automáticamente.",step1_label:"Servicio meteorológico — de dónde obtener los datos meteorológicos",step2_label:"Módulo de cálculo — cómo se calcula la duración del riego",step3_label:"Grupo de sensores — qué fuentes de datos usar",step4_label:"Zona — tu primera zona de riego",tip:"Puedes omitir cualquier paso y configurarlo más tarde desde la pestaña Configuración."},weather:{title:"Servicio meteorológico",description:"Elige cómo obtener los datos meteorológicos. Open-Meteo es gratuito y no requiere clave API — es la opción más sencilla para la mayoría."},module:{title:"Módulo de cálculo",description:"Un módulo calcula cuánto regar según la evapotranspiración (ET). El módulo PyETO (método FAO-56) es el recomendado para la mayoría.",pick_label:"Seleccionar tipo de módulo",no_modules:"No hay tipos de módulo disponibles."},mapping:{title:"Grupo de sensores",description:"Un grupo de sensores vincula cada variable meteorológica con una fuente de datos. Define las variables clave a continuación — podrás refinar las asignaciones de sensores individuales más tarde en la pestaña Configuración → Grupos de sensores.",name_label:"Nombre del grupo de sensores",source_label:"Fuente de datos para",use_weather_service:"Servicio meteorológico",use_sensor:"Sensor",use_static:"Valor estático",use_none:"Ninguna / sin usar"},zone:{title:"Primera zona",description:"Una zona es un área de riego (p. ej. césped, parterre). Define las propiedades físicas para que el sistema pueda calcular la duración de riego correcta.",name_label:"Nombre de la zona",size_label:"Superficie",throughput_label:"Caudal del aspersor",entity_label:"Interruptor o válvula vinculados",entity_placeholder:"p. ej. switch.garden_valve",module_label:"Módulo de cálculo",mapping_label:"Grupo de sensores"},done:{title:"¡Configuración completada!",description:"Tu primera zona está lista. Smart Irrigation ahora calculará las duraciones de riego automáticamente según los datos meteorológicos.",next_steps:"Qué puedes hacer a continuación:",tip1:"Ve a Zonas para ver las duraciones calculadas y los valores del depósito.",tip2:"Añade más zonas desde la pestaña Zonas.",tip3:"Ajusta todos los parámetros desde la pestaña Configuración.",go_zones:"Ir a Zonas",go_setup:"Ir a Configuración"}}},Ea={common:ma,defaults:va,module:fa,calcmodules:_a,panels:ba,title:ya,coordinate_config:wa,days_between_irrigation:ka,irrigation_start_triggers:za,weather_skip:Sa,zone_sequencing:xa,weather_service_config:$a,field_help:Aa,wizard:Ma},Ta=Object.freeze({__proto__:null,common:ma,defaults:va,module:fa,calcmodules:_a,panels:ba,title:ya,coordinate_config:wa,days_between_irrigation:ka,irrigation_start_triggers:za,weather_skip:Sa,zone_sequencing:xa,weather_service_config:$a,field_help:Aa,wizard:Ma,default:Ea}),Da={actions:{delete:"Suppression",edit:"Modifier",save:"Enregistrer",cancel:"Annuler",confirm_delete:"Confirmer la suppression",confirm_delete_zone:"Voulez-vous vraiment supprimer cette zone ?"},labels:{module:"Module",no:"Non",select:"Sélectionner",yes:"Oui",enabled:"Activé",disabled:"Désactivé",before:"avant",after:"après",settings:"Paramètres",bulk_actions:"Actions groupées"},attributes:{size:"taille",throughput:"débit",state:"état",bucket:"réservoir",last_updated:"dernière mise à jour",last_calculated:"dernier calcul",number_of_data_points:"nombre de points de données"},loading:"Chargement",saving:"Enregistrement",units:{seconds:"secondes"},"loading-messages":{configuration:"Chargement de la configuration...",modules:"Chargement des modules...",general:"Chargement..."},"saving-messages":{adding:"Ajout...",saving:"Enregistrement..."},errors:{load_failed:"Impossible de charger les données",save_failed:"Impossible d'enregistrer les modifications",delete_failed:"Impossible de supprimer",action_failed:"Échec de l'action"}},ja={"default-zone":"Zone par défaut","default-mapping":"Groupe de capteurs par défaut"},Oa={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"NB: cette explication utilise '.' comme séparateur décimal, et affiche des valeurs arrondies. Le module a donné un manque d'Évapotranspiration de","bucket-was":"Le seau (bucket) était de","new-bucket-values-is":"La nouvelle valeur du seau (bucket) est","old-bucket-variable":"ancien_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Puisque le seau (bucket) est < 0, l'irrigation est nécessaire","steps-taken-to-calculate-duration":"Pour calculer la durée d'irrigation, les étapes suivantes ont été réalisées","precipitation-rate-defined-as":"Le taux de précipitation est défini comme","duration-is-calculated-as":"La durée d'irrigation est calculée avec",bucket:"seau (bucket)","precipitation-rate-variable":"taux_precipitation","multiplier-is-applied":"Le multiplicateur est appliqué. Le multiplicateur est","duration-after-multiplier-is":"donc la durée d'irrigation est de","maximum-duration-is-applied":"Ensuite la durée maximale est appliquée. La durée maximale est de","duration-after-maximum-duration-is":"donc la durée d'irrigation est de","lead-time-is-applied":"Enfin, le délai est appliqué. Le délai est de","duration-after-lead-time-is":"et donc la durée finale est de","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Puisque le seau (bucket) est >= 0, l'irrigation n'est pas nécessaire, et la durée est réglée à","maximum-bucket-is":"la taille du seau (bucket) maximale est","max-bucket-variable":"max_bucket",drainage:"drainage","drainage-rate":"taux de drainage",hours:"heures","drainage-rate-is":"Le taux de drainage à saturation (réservoir au maximum) est","current-drainage-is":"Le drainage actuel est calculé comme","no-drainage":"Le drainage actuel est 0 parce que"}}},Ca={pyeto:{description:"Le calcul de durée est basée sur le calcul FAO56 de la bibliothèque PyETO"},static:{description:"Module 'Dummy' avec un delta statique configurable"},passthrough:{description:"Module passerelle qui renvoie la valeur d'un capteur d'Évapotranspiration comme delta"}},Pa={general:{cards:{"automatic-duration-calculation":{header:"Calcul automatique de la durée",labels:{"auto-calc-enabled":"Calcule automatiquement la durée par zone","auto-calc-time":"Calcule à","calc-time":"Calculer à"},description:"Le calcul prend en compte les données météo jusqu'à ce point et met à jour le seau (bucket) pour chaque zone automatique. Ensuite, la durée est ajustée par la nouvelle valeur de seau (bucket) et les données météo sont supprimées."},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Attention: mise à jour des données météo au moment du, ou après le, calcul"},header:"Mise à jour automatique des données météo",labels:{"auto-update-enabled":"Met à jour les données météo automatiquement","auto-update-first-update":"(Première) Mise à jour à","auto-update-interval":"Mettre à jour les données des capteurs toutes les","auto-update-delay":"Délai de mise à jour","auto-update-schedule":"Planning de mise à jour","auto-update-time":"Mettre à jour à"},options:{days:"jours",hours:"heures",minutes:"minutes"},description:"Récupère et stocke les données météo automatiquement. Des données météo sont nécessaires pour calculer les seaux (buckets) par zone et les durées."},"automatic-clear":{header:"Délestage automatique des données météo",description:"Suppression automatique des données météo collectées à une heure données. Utilisez ceci pour être sûr qu'il n'y ait plus de restes des données météo des jours précédents. Ne supprimez pas les données météo avant le calcul et n'utilisez cette option que si vous vous attendez à ce que les données météo soient récupérées après le calcul du jour. Idéalement, vous voudrez \"élaguer\" les données les plus tard possible dans la journée.",labels:{"automatic-clear-enabled":"Suppression automatique des données météo collectées","automatic-clear-time":"Supprimer les données météo à"}},continuousupdates:{header:"Mises à jour continues des capteurs (expérimental)",description:"Fonction expérimentale pour des données météo plus granulaires.",labels:{continuousupdates:"Activer les mises à jour continues",sensor_debounce:"Anti-rebond du capteur","sensor-debounce":"Temps d'antirebond du capteur (ms)"}}},description:"Cette page fournit les réglages globaux.",title:"Général"},help:{title:"Aide",cards:{"how-to-get-help":{title:"Comment obtenir de l'aide","first-read-the":"Premièrement, lisez ",wiki:"Documentation","if-you-still-need-help":"Si vous avez toujours besoin d'aide, adressez vous sur le","community-forum":"forum communautaire","or-open-a":"ou ouvrez un","github-issue":"problème Github","english-only":"en Anglais uniquement"}}},mappings:{cards:{"add-mapping":{actions:{add:"Ajouter un groupe de capteurs"},header:"Ajouter des groupes de capteurs"},mapping:{aggregates:{average:"Moyenne",first:"Premier",last:"Dernier",maximum:"Maximum",median:"Médian",minimum:"Minimum",sum:"Somme",riemannsum:"Somme de Riemann",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"Vous ne pouvez pas supprimer ce groupe de capteurs car au moins une zone l'utilise.",invalid_source:"Source invalide",source_does_not_exist:"La source n'existe pas. Veuillez saisir une source valide, comme 'sensor.mysensor'."},items:{dewpoint:"Point de rosée",evapotranspiration:"Évapotranspiration",humidity:"Humidité","maximum temperature":"Température maximale","minimum temperature":"Température minimale",precipitation:"Précipitation totale",pressure:"Pression","solar radiation":"Rayonnement solaire",temperature:"Température",windspeed:"Vitesse du vent","current precipitation":"Précipitations actuelles"},"sensor-aggregate-of-sensor-values-to-calculate":"des valeurs des capteurs pour calculer la durée","sensor-aggregate-use-the":"Utiliser les","sensor-entity":"Entité capteur",static_value:"Valeur","input-units":"L'entité fournit des entrées en",source:"Source",sources:{none:"Aucun",weather_service:"Service météo",sensor:"Capteur",static:"Valeur statique"},pressure_types:{relative:"relative",absolute:"absolue"},"pressure-type":"La pression est","sensor-units":"Le capteur fournit les valeurs en"}},description:"Ajouter un ou plusieurs groupes de capteurs qui récupèrent les données météo de Weather service, de capteurs locaux ou d'une combinaison de tous ceux-ci. Vous pouvez associer chaque groupe de capteurs avec une ou plusieurs zones",labels:{"mapping-name":"Nom"},no_items:"Il n'y a pas encore de groupe de capteurs définis.",title:"Groupes de capteurs","weather-records":{title:"Relevés météo",timestamp:"Heure",temperature:"Temp.",humidity:"Humidity",precipitation:"Précip.","retrieval-time":"Récupéré","no-data":"Aucune donnée météo disponible pour ce groupe de capteurs",dewpoint:"Rosée",wind:"Vent",pressure:"Pression"}},modules:{cards:{"add-module":{actions:{add:"Ajouter un module"},header:"Ajout d'un module"},module:{errors:{"cannot-delete-module-because-zones-use-it":"Vous ne pouvez pas supprimer ce module car au moins une zone l'utilise."},labels:{configuration:"Configuration",required:"indique un champ requis"},"translated-options":{DontEstimate:"Ne fait pas d'estimation",EstimateFromSunHours:"Estimation à partir des heures d'ensoleillement",EstimateFromTemp:"Estimation à partir de la température",EstimateFromSunHoursAndTemperature:"Estimer à partir de la moyenne des heures d'ensoleillement et de la température"}}},description:"Ajouter un ou plusieurs modules qui calcule la durée d'irrigation. Chaque module vient avec sa propre configuration et peut être utilisé pour calculer la durée d'irrigation d'une ou plusieurs zones.",no_items:"Il n'y a aucun module défini pour l'instant.",title:"Modules"},zones:{actions:{add:"Ajouter",calculate:"Calculer",information:"Informations",update:"Mise à jour","reset-bucket":"Mise à zéro du seau (bucket)","view-weather-info":"Voir données météo","view-weather-info-message":"Données météo disponibles pour","view-watering-calendar":"Calendrier d'arrosage",irrigate_all:"Lancer toutes les zones maintenant"},cards:{"add-zone":{actions:{add:"Ajouter une zone"},header:"Ajout d'une zone"},"zone-actions":{actions:{"calculate-all":"Calculer pour toutes les zones","update-all":"Mise à jour de toutes les zones","reset-all-buckets":"Mise à zéro de tous les seaux (buckets)","clear-all-weatherdata":"Mise à zéro de toutes les données météo"},header:"Actions sur toutes les zones"}},description:"Spécifiez une ou plusieurs zones d'irrigation ici. La durée d'irrigation est calculée par zone, en fonction de la taille, du débit, état, module et groupe de capteurs.",labels:{bucket:"Seau",duration:"Durée","lead-time":"Délai",mapping:"Groupe de capteurs","maximum-duration":"Durée maximale",multiplier:"Multiplicateur",name:"Nom",size:"Taille",state:"État",states:{automatic:"Automatique",disabled:"Désactivé",manual:"Manuel"},throughput:"Débit","maximum-bucket":"Seau (bucket) maximum",last_calculated:"Dernier calcul","data-last-updated":"Dernière mise à jour","data-number-of-data-points":"Nombre de points de données",drainage_rate:"Taux de drainage",linked_entity:"Entité interrupteur/vanne liée",linked_entity_placeholder:"ex. switch.vanne_jardin",irrigate_now:"Irriguer maintenant",bucket_threshold:"Déficit minimum pour irriguer",flow_sensor:"Capteur de débitmètre (optionnel)",flow_sensor_placeholder:"p. ex. sensor.zone_flow_rate"},no_items:"Il n'y a pas encore de zone définie.",title:"Zones",confirm_irrigate:{title:"Démarrer l'arrosage ?",body:"Ceci ouvre maintenant la ou les vannes liées et ignore toutes les conditions d'exclusion (pluie, température, nombre minimal de jours entre les arrosages).",all_linked_zones:"Toutes les zones liées",toast_started:"Arrosage démarré",toast_failed:"Échec de l'arrosage"}},schedules:{title:"Planifications",description:"Créez des planifications récurrentes pour calculer, mettre à jour ou irriguer automatiquement — sans automatisations.",add:"Ajouter une planification",no_items:"Aucune planification configurée. Cliquez sur 'Ajouter une planification'.",zones_all:"Toutes les zones",zones_specific:"Zones spécifiques",hours:"heures",minutes:"min",types:{daily:"Quotidien",weekly:"Hebdomadaire",monthly:"Mensuel",interval:"Toutes les N heures",sunrise:"Lever du soleil",sunset:"Coucher du soleil",solar_azimuth:"Azimut solaire"},actions:{calculate:"Calculer (mettre à jour la durée d'irrigation)",update:"Mettre à jour (collecter données météo)",irrigate:"Irriguer (contrôler les vannes directement)"},days:{monday:"Lu",tuesday:"Ma",wednesday:"Me",thursday:"Je",friday:"Ve",saturday:"Sa",sunday:"Di"},fields:{name:"Nom",type:"Type de planification",enabled:"Activé",time:"Heure (HH:MM)",days_of_week:"Jours de la semaine",day_of_month:"Jour du mois",interval_hours:"Intervalle",action:"Action",zones:"Zones",start_date:"Date de début (optionnel)",end_date:"Date de fin (optionnel)",offset_minutes:"Décalage par rapport au lever/coucher du soleil",account_for_duration:"Démarrer tôt pour que l'irrigation se termine à l'heure cible",azimuth_angle:"Angle d'azimut solaire"},dialog:{add_title:"Ajouter une planification",edit_title:"Modifier la planification"}},info:{title:"Infos",description:"Afficher les informations sur la prochaine irrigation et l'état du système.","configuration-not-available":"Configuration non disponible.",cards:{"zone-bucket-values":{title:"Valeurs de réservoir et durée",labels:{bucket:"Réservoir",duration:"Durée"},"no-zones":"Aucune zone configurée"},"next-irrigation":{title:"Prochaine irrigation",labels:{"next-start":"Prochain démarrage",duration:"Durée",zones:"Zones"},"no-data":"Aucune donnée disponible"},"irrigation-reason":{title:"Raison d'irrigation",labels:{reason:"Raison",sunrise:"Lever du soleil","total-duration":"Durée totale",explanation:"Explication"},"no-data":"Aucune donnée disponible"},irrigate_now:{title:"Irriguer maintenant",description:"Démarrer immédiatement l'irrigation pour toutes les zones avec une entité liée. Les conditions d'exclusion sont ignorées.",button_all:"Démarrer toutes les zones maintenant",no_linked_zones:"Aucune zone n'a d'entité interrupteur/vanne liée avec une durée calculée."}}},setup:{title:"Configuration"}},Na="Smart Irrigation",Ha={title:"Coordonnées de Localisation",description:"Configurez les coordonnées de localisation pour la récupération des données météo. Vous pouvez utiliser des coordonnées manuelles différentes de votre emplacement Home Assistant si nécessaire.",manual_enabled:"Utiliser des coordonnées manuelles",use_ha_location:"Utiliser l'emplacement Home Assistant",latitude:"Latitude (degrés décimaux)",longitude:"Longitude (degrés décimaux)",elevation:"Élévation (mètres au-dessus du niveau de la mer)",current_ha_coords:"Coordonnées actuelles de Home Assistant"},Ia={title:"Jours entre irrigations",description:"Configurez le nombre minimum de jours entre les événements d'irrigation.",label:"Jours minimum entre irrigations",help_text:"Définissez 0 pour désactiver. Les valeurs de 1 à 365 jours sont supportées."},La={title:"Déclencheurs de démarrage d'arrosage",description:"Configurez le moment où l'arrosage doit démarrer en fonction des événements solaires. Vous pouvez ajouter plusieurs déclencheurs pour différents horaires. Pour les déclencheurs au lever du soleil, laisser le décalage à 0 utilisera automatiquement la durée totale de toutes les zones activées.",add_trigger:"Ajouter un déclencheur",edit_trigger:"Modifier le déclencheur",delete_trigger:"Supprimer le déclencheur",trigger_types:{sunrise:"Lever du soleil",sunset:"Coucher du soleil",solar_azimuth:"Azimut solaire"},fields:{name:{name:"Nom du déclencheur",description:"Un nom descriptif pour identifier ce déclencheur"},type:{name:"Type de déclencheur",description:"Le type d'événement solaire qui déclenche"},enabled:{name:"Activé",description:"Si ce déclencheur est actuellement actif"},offset_minutes:{name:"Décalage (minutes)",description:"Minutes avant (-) ou après (+) l'événement solaire. Pour les déclencheurs au lever du soleil, utilisez 0 pour une temporisation automatique basée sur la durée totale des zones."},azimuth_angle:{name:"Angle d'azimut (degrés)",description:"Angle d'azimut solaire en degrés où 0=Nord, 90=Est, 180=Sud, 270=Ouest"},account_for_duration:{name:"Tenir compte de la durée",description:"Si activé, l'arrosage démarrera suffisamment tôt pour se terminer à l'heure indiquée. Si désactivé, l'arrosage démarrera exactement à l'heure indiquée."}},dialog:{add_title:"Ajouter un déclencheur de démarrage d'arrosage",edit_title:"Modifier le déclencheur de démarrage d'arrosage",cancel:"Annuler",save:"Enregistrer",delete:"Supprimer"},no_triggers:"Aucun déclencheur de démarrage d'arrosage configuré. Le système utilisera le comportement par défaut (lever du soleil avec la durée totale des zones). Ajoutez des déclencheurs pour personnaliser le démarrage de l'arrosage.",offset_auto:"Automatique (calculé à partir de la durée totale des zones)",confirm_delete:"Voulez-vous vraiment supprimer le déclencheur '{name}' ?",validation:{name_required:"Le nom du déclencheur est requis",azimuth_invalid:"L'angle d'azimut doit être un nombre valide"},help:{sunrise_offset:"Pour les déclencheurs au lever du soleil : utilisez des valeurs négatives pour démarrer avant le lever, positives pour démarrer après. Mettez 0 pour démarrer automatiquement assez tôt pour terminer toutes les zones avant le lever du soleil.",sunset_offset:"Pour les déclencheurs au coucher du soleil : utilisez des valeurs négatives pour démarrer avant le coucher, positives pour démarrer après.",azimuth_explanation:"L'azimut solaire est la direction de la boussole du soleil. 0°=Nord, 90°=Est, 180°=Sud, 270°=Ouest. Vous pouvez saisir n'importe quelle valeur d'angle (p. ex. 450° = 90°, -30° = 330°). Utilisez ceci pour déclencher l'arrosage lorsque le soleil atteint une position précise.",multiple_triggers:"Vous pouvez configurer plusieurs déclencheurs. Chaque déclencheur activé planifiera les démarrages d'arrosage de manière indépendante."}},Ba={title:"Conditions d'exclusion",description:"Ignorer automatiquement l'irrigation quand les conditions sont défavorables. Les vérifications de précipitations, température et vent nécessitent un service météo.",threshold_label:"Seuil de précipitations",threshold_description:"Quantité minimale de précipitations prévues (en mm) pour aujourd'hui et demain pour ignorer l'irrigation.",temp_section_title:"Ignorer par basse température",temp_threshold_label:"Ignorer si température en dessous de",wind_section_title:"Ignorer par vent fort",wind_threshold_label:"Ignorer si vitesse du vent supérieure à",rain_sensor_section_title:"Condition du capteur de pluie",rain_sensor_label:"Entité capteur de pluie (optionnel)",rain_sensor_placeholder:"ex. binary_sensor.pluie"},Ua={title:"Séquençage des zones",description:"Lorsque plusieurs zones ont besoin d'irrigation, choisissez si elles fonctionnent simultanément ou l'une après l'autre. En mode séquentiel, le système attend que chaque zone se termine avant de démarrer la suivante.",parallel:"Parallèle (toutes les zones simultanément)",sequential:"Séquentiel (une zone à la fois)",rotating:"Rotatif (les zones se relaient)",max_consecutive_duration_label:"Durée d'exécution consécutive max. par zone",max_consecutive_duration_unit:"minutes",min_absorption_time_label:"Temps d'absorption min. entre les passages",min_absorption_time_unit:"minutes (0 = désactivé)"},Ra={title:"Service météo",description:"Configurez le service météo à utiliser pour les calculs d'ET et les conditions de saut.",enabled_label:"Activer le service météo",service_label:"Service météo",api_key_label:"Clé API",api_key_placeholder:"Laisser vide pour conserver la clé existante",api_key_configured:"La clé API est configurée",api_key_not_configured:"Aucune clé API configurée",api_key_help:"Une clé API de votre fournisseur de service météo choisi. Open-Meteo ne nécessite pas de clé. OpenWeatherMap et Pirate Weather offrent tous deux des offres gratuites.",no_api_key_needed:"Open-Meteo est un service gratuit et ne nécessite aucune clé API.",save_button:"Enregistrer les paramètres météo",saved:"Paramètres météo enregistrés",openmeteo:"Open-Meteo (gratuit, sans clé)",test_button:"Tester la connexion",test_button_testing:"Test en cours…",test_success:"✓ Connexion réussie",test_error_invalid_auth:"✗ Clé API invalide — vérifiez qu'elle est correcte et active",test_error_cannot_connect:"✗ Connexion impossible — vérifiez votre connexion internet",test_error_no_service:"✗ Sélectionnez d'abord un service météo",test_error_unknown:"✗ Échec du test — erreur inconnue",owm:"OpenWeatherMap",pw:"Pirate Weather"},Wa={zone_size:"La surface arrosée totale de cette zone. Utilisée avec le débit pour calculer la quantité d'eau appliquée par passage.",zone_throughput:"Débit d'eau total de votre système d'arrosage pour cette zone (litres/min en métrique, gal/min en impérial). Consultez la fiche technique de vos arroseurs ou mesurez le temps nécessaire pour remplir un récipient de volume connu.",zone_drainage_rate:"La vitesse à laquelle l'eau excédentaire s'évacue du sol lorsque le réservoir est plein. Typique : pelouse 50 mm/h, sol sableux 100+ mm/h, argile 10 mm/h.",zone_bucket:"Déficit (négatif) ou excédent (positif) d'eau actuel de cette zone. L'arrosage se déclenche lorsque le réservoir descend sous le seuil.",zone_maximum_bucket:"Excédent d'humidité maximal que la zone peut retenir. L'eau au-delà de ce niveau est considérée comme du ruissellement. Valeur typique : 50 mm.",zone_bucket_threshold:"L'arrosage se déclenche lorsque le réservoir descend sous cette valeur. Doit être 0 ou négatif. 0 signifie arroser dès qu'il y a un déficit.",zone_multiplier:"Facteur d'échelle appliqué à la durée calculée. Au-dessus de 1,0 pour augmenter, en dessous de 1,0 pour diminuer. Utile pour un réglage fin sans modifier les mesures physiques.",zone_lead_time:"Secondes supplémentaires avant le démarrage de l'arrosage. À utiliser pour la mise en chauffe de la pompe ou la mise en pression du système.",zone_maximum_duration:"Plafond strict pour un seul passage d'arrosage en secondes. Empêche un arrosage incontrôlé. Par défaut : 3600 s (1 heure).",zone_linked_entity:"L'entité interrupteur ou vanne de HA qui contrôle le débit d'eau de cette zone. Cette entité est activée lorsque l'arrosage fonctionne.",zone_flow_sensor:"Capteur optionnel mesurant le débit d'eau réel. Utilisé uniquement pour le rapport — n'affecte pas les calculs de durée.",general_autoupdatedelay:"Secondes à attendre après le démarrage de HA avant la première récupération des données météo. Permet aux autres intégrations de s'initialiser d'abord.",general_sensor_debounce:"Écart minimal en millisecondes entre les lectures du capteur pour filtrer le bruit des capteurs qui changent rapidement.",general_calctime:"Heure de la journée à laquelle les durées d'arrosage sont recalculées à partir des données météo collectées. Format : HH:MM (24 heures).",general_cleardatatime:"Heure de la journée à laquelle les anciennes données météo sont purgées. Doit être réglée après l'heure de calcul.",general_days_between:"Nombre minimal de jours entre les arrosages d'une même zone. Mettre 0 pour désactiver (arroser dès qu'il y a un déficit).",general_autoupdateinterval:"Fréquence de collecte des données météo. Choisissez une valeur qui équilibre la fraîcheur des données et les limites de l'API.",general_precipitation_threshold:"L'arrosage est ignoré si les précipitations prévues pour aujourd'hui/demain dépassent cette valeur.",general_temp_threshold:"L'arrosage est ignoré si la température actuelle est inférieure à cette valeur (p. ex. pour éviter les dégâts du gel).",general_wind_threshold:"L'arrosage est ignoré si la vitesse du vent dépasse cette valeur (un vent fort réduit l'efficacité et provoque une dérive)."},Fa={title:"Assistant de configuration",open_button:"Assistant de configuration",close:"Fermer",next:"Suivant",back:"Retour",finish:"Terminer",skip_step:"Ignorer cette étape",step_indicator:"Étape {current} sur {total}",setup_complete_banner:"Configuration non terminée. Lancez l'assistant pour commencer.",open_wizard:"Ouvrir l'assistant",steps:{welcome:{title:"Bienvenue dans Smart Irrigation",intro:"Cet assistant vous guide à travers les quatre étapes nécessaires pour que votre première zone arrose automatiquement.",step1_label:"Service météo — où obtenir les données météo",step2_label:"Module de calcul — comment la durée d'arrosage est calculée",step3_label:"Groupe de capteurs — quelles sources de données utiliser",step4_label:"Zone — votre première zone d'arrosage",tip:"Vous pouvez ignorer n'importe quelle étape et la configurer plus tard depuis l'onglet Configuration."},weather:{title:"Service météo",description:"Choisissez comment obtenir les données météo. Open-Meteo est gratuit et ne nécessite pas de clé API — c'est le choix le plus simple pour la plupart des utilisateurs."},module:{title:"Module de calcul",description:"Un module calcule la durée d'arrosage en fonction de l'évapotranspiration (ET). Le module PyETO (méthode FAO-56) est recommandé pour la plupart des utilisateurs.",pick_label:"Sélectionner le type de module",no_modules:"Aucun type de module disponible."},mapping:{title:"Groupe de capteurs",description:"Un groupe de capteurs relie chaque variable météo à une source de données. Définissez les variables clés ci-dessous — vous pourrez affiner chaque association de capteur plus tard depuis l'onglet Configuration → Groupes de capteurs.",name_label:"Nom du groupe de capteurs",source_label:"Source de données pour",use_weather_service:"Service météo",use_sensor:"Capteur",use_static:"Valeur statique",use_none:"Aucune / non utilisé"},zone:{title:"Première zone",description:"Une zone est une surface d'arrosage (p. ex. pelouse, massif). Définissez les propriétés physiques pour que le système puisse calculer la durée d'arrosage correcte.",name_label:"Nom de la zone",size_label:"Surface",throughput_label:"Débit de l'arroseur",entity_label:"Interrupteur ou vanne lié",entity_placeholder:"p. ex. switch.garden_valve",module_label:"Module de calcul",mapping_label:"Groupe de capteurs"},done:{title:"Configuration terminée !",description:"Votre première zone est prête. Smart Irrigation calculera désormais les durées d'arrosage automatiquement à partir des données météo.",next_steps:"Ce que vous pouvez faire ensuite :",tip1:"Allez dans Zones pour voir les durées calculées et les valeurs du réservoir.",tip2:"Ajoutez d'autres zones depuis l'onglet Zones.",tip3:"Affinez tous les paramètres depuis l'onglet Configuration.",go_zones:"Aller aux Zones",go_setup:"Aller à la Configuration"}}},qa={common:Da,defaults:ja,module:Oa,calcmodules:Ca,panels:Pa,title:Na,coordinate_config:Ha,days_between_irrigation:Ia,irrigation_start_triggers:La,weather_skip:Ba,zone_sequencing:Ua,weather_service_config:Ra,field_help:Wa,wizard:Fa},Va=Object.freeze({__proto__:null,common:Da,defaults:ja,module:Oa,calcmodules:Ca,panels:Pa,title:Na,coordinate_config:Ha,days_between_irrigation:Ia,irrigation_start_triggers:La,weather_skip:Ba,zone_sequencing:Ua,weather_service_config:Ra,field_help:Wa,wizard:Fa,default:qa}),Za={actions:{delete:"Cancella",edit:"Modifica",save:"Salva",cancel:"Annulla",confirm_delete:"Conferma eliminazione",confirm_delete_zone:"Vuoi davvero eliminare questa zona?"},labels:{module:"Modulo",no:"No",select:"Seleziona",yes:"Si",enabled:"Abilitato",disabled:"Disabilitato",before:"prima",after:"dopo",settings:"Impostazioni",bulk_actions:"Azioni multiple"},units:{seconds:"secondi"},attributes:{size:"dimensione",throughput:"portata",state:"stato",bucket:"serbatoio",last_updated:"ultimo aggiornamento",last_calculated:"ultimo calcolo",number_of_data_points:"numero di punti dati"},loading:"Caricamento",saving:"Salvataggio","loading-messages":{configuration:"Caricamento configurazione...",modules:"Caricamento moduli...",general:"Caricamento..."},"saving-messages":{adding:"Aggiungendo...",saving:"Salvataggio..."},errors:{load_failed:"Impossibile caricare i dati",save_failed:"Impossibile salvare le modifiche",delete_failed:"Impossibile eliminare",action_failed:"Azione non riuscita"}},Ya={"default-zone":"Zona predefinita","default-mapping":"Mappatura predefinita"},Ga={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Il modulo ha restituito un deficit di evapotraspirazione del","bucket-was":"Il secchio era","new-bucket-values-is":"Il nuovo valore del secchio è",bucket:"secchio","old-bucket-variable":"old_bucket","max-bucket-variable":"max_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Poiché secchio < 0, è necessaria l'irrigazione","steps-taken-to-calculate-duration":"Per calcolare la durata esatta, sono stati eseguiti i seguenti passaggi","precipitation-rate-defined-as":"Il tasso di precipitazione è definito come","duration-is-calculated-as":"La durata viene calcolata come",drainage:"drenaggio","drainage-rate":"tasso_di_drenaggio",hours:"ore","precipitation-rate-variable":"tasso_di_precipitazione","multiplier-is-applied":"Ora viene applicato il moltiplicatore. Il moltiplicatore è","duration-after-multiplier-is":"quindi la durata è","maximum-duration-is-applied":"Quindi, viene applicata la durata massima. La durata massima è","duration-after-maximum-duration-is":"quindi la durata è","lead-time-is-applied":"Infine, viene applicato il lead time. Il tempo di consegna è","duration-after-lead-time-is":"quindi la durata finale è","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Poiché secchio >= 0, non è necessaria alcuna irrigazione e la durata è impostata su","maximum-bucket-is":"la dimensione massima del secchio è","drainage-rate-is":"Il tasso di drenaggio a saturazione (serbatoio al massimo) è","current-drainage-is":"Il drenaggio attuale è calcolato come","no-drainage":"Il drenaggio attuale è 0 perché"}}},Ka={pyeto:{description:"Calcola la durata in base al calcolo FAO56 dalla libreria PyETO"},static:{description:"Modulo 'fittizio' con un delta configurabile statico"},passthrough:{description:"Modulo passthrough che restituisce il valore di un sensore di Evapotraspirazione sotto forma di delta"}},Xa={general:{cards:{"automatic-duration-calculation":{header:"Calcolo automatico della durata",description:"Il calcolo prende i dati meteorologici raccolti fino a quel momento e aggiorna il bucket per ciascuna zona automatica. Quindi, la durata viene regolata in base al nuovo valore del segmento e i dati meteorologici raccolti vengono rimossi.",labels:{"auto-calc-enabled":"Calcola automaticamente la durata delle zone","auto-calc-time":"Calcola a","calc-time":"Calcola alle"}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Attenzione: ora di aggiornamento dei dati meteorologici in corrispondenza o dopo l'ora di calcolo"},header:"Aggiornamento automatico dei dati meteorologici",description:"Raccogli e archivia automaticamente i dati meteorologici. I dati meteorologici sono necessari per calcolare gli intervalli e le durate delle zone.",labels:{"auto-update-enabled":"Aggiorna automaticamente i dati meteorologici","auto-update-first-update":"(Primo) aggiornamento alle","auto-update-interval":"Aggiorna i dati del sensore ogni","auto-update-schedule":"Pianificazione aggiornamento","auto-update-time":"Aggiorna alle","auto-update-delay":"Ritardo di aggiornamento"},options:{days:"giorni",hours:"ore",minutes:"minuti"}},"automatic-clear":{header:"Eliminazione automatica dei dati meteo",description:"Rimuovi automaticamente i dati meteo raccolti a un orario configurato. Usa questa opzione per assicurarti che non vi siano dati meteo residui dei giorni precedenti. Non rimuovere i dati meteo prima di effettuare il calcolo e utilizza questa opzione solo se prevedi che l'aggiornamento automatico raccolga i dati meteo dopo aver effettuato il calcolo giornaliero. Idealmente, la rimozione dei dati meteo dovrebbe avvenire il più tardi possibile.",labels:{"automatic-clear-enabled":"Cancella automaticamente i dati meteorologici raccolti","automatic-clear-time":"Cancella dati meteo a"}},continuousupdates:{header:"Aggiornamenti continui sensori (sperimentale)",description:"Funzione sperimentale per dati meteo più granulari.",labels:{continuousupdates:"Abilita gli aggiornamenti continui",sensor_debounce:"Rimbalzo del sensore","sensor-debounce":"Tempo anti-rimbalzo sensore (ms)"}}},description:"Questa pagina fornisce le impostazioni globali.",title:"Generale"},help:{title:"Aiuto",cards:{"how-to-get-help":{title:"Come ottenere aiuto","first-read-the":"Per prima cosa, leggi il",wiki:"Documentazione","if-you-still-need-help":"Se hai ancora bisogno di aiuto, contatta il","community-forum":"Forum della Comunità","or-open-a":"oppure apri un","github-issue":"Problema su Github","english-only":"soltanto in Inglese"}}},info:{title:"Info",description:"Visualizza informazioni sulla prossima irrigazione e lo stato del sistema.",cards:{"next-irrigation":{title:"Prossima irrigazione",labels:{"next-start":"Prossimo avvio",duration:"Durata",zones:"Zone"},"no-data":"Nessun dato disponibile","backend-todo":"TODO: API di backend necessaria per le informazioni sull'irrigazione"},"irrigation-reason":{title:"Motivo irrigazione",labels:{reason:"Ragione",sunrise:"Alba","total-duration":"Durata totale",explanation:"Spiegazione"},"no-data":"Nessun dato disponibile","backend-todo":"TODO: API di backend necessaria per le informazioni sull'irrigazione"},"zone-bucket-values":{title:"Valori serbatoio e durata",labels:{bucket:"Serbatoio",duration:"Durata"},"no-zones":"Nessuna zona configurata"},irrigate_now:{title:"Irriga ora",description:"Avvia immediatamente l'irrigazione per tutte le zone con entità collegata. Le condizioni di esclusione vengono ignorate.",button_all:"Avvia tutte le zone ora",no_linked_zones:"Nessuna zona ha un'entità interruttore/valvola collegata con durata calcolata."}},"configuration-not-available":"Configurazione non disponibile."},mappings:{cards:{"add-mapping":{actions:{add:"Aggiungi gruppo di sensori"},header:"Aggiungi gruppo di sensori"},mapping:{aggregates:{average:"Media",first:"Primo",last:"Ultimo",maximum:"Massimo",median:"Mediana",minimum:"Minimo",riemannsum:"Somma di Riemann",sum:"Somma",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"Non è possibile eliminare questo gruppo di sensori perché almeno una zona lo utilizza.",invalid_source:"Fonte non valida",source_does_not_exist:"La fonte non esiste. Inserire una fonte valida, ad esempio 'sensor.mysensor'."},items:{dewpoint:"Punto di rugiada",evapotranspiration:"Evapotraspirazione",humidity:"Umidità","maximum temperature":"Temperatura massima","minimum temperature":"Temperatura minima",precipitation:"Precipitazione","current precipitation":"Precipitazioni attuali",pressure:"Pressione","solar radiation":"Irradiamento solare",temperature:"Temperatura",windspeed:"Velocità del vento"},pressure_types:{absolute:"assoluta",relative:"relativa"},"pressure-type":"La pressione è","sensor-aggregate-of-sensor-values-to-calculate":"dei valori del sensore per calcolare la durata","sensor-aggregate-use-the":"Usa il","sensor-entity":"Entità sensore",static_value:"Valore","input-units":"L'input fornisce valori in",source:"Fonte",sources:{none:"Nessuna",weather_service:"Servizio meteo",sensor:"Sensore",static:"Valore statico"}}},description:"Aggiungi uno o più gruppi di sensori che recuperano i dati meteorologici da Weather service, da sensori o da una combinazione di questi. È possibile mappare ciascun gruppo di sensori su una o più zone",labels:{"mapping-name":"Nome"},no_items:"Non è ancora stato definito alcun gruppo di sensori.",title:"Gruppi di sensori","weather-records":{title:"Record meteo (ultimi 10)",timestamp:"Tempo",temperature:"Temp.",humidity:"Umidità",precipitation:"Precip.","retrieval-time":"Recuperato","no-data":"Non sono disponibili dati meteo per questo gruppo di sensori",dewpoint:"Rugiada",wind:"Vento",pressure:"Press."}},modules:{cards:{"add-module":{actions:{add:"Aggiungi modulo"},header:"Aggiungi modulo"},module:{errors:{"cannot-delete-module-because-zones-use-it":"Non puoi eliminare questo modulo perché almeno una zona lo utilizza."},labels:{configuration:"Configurazione",required:"indica un campo richiesto"},"translated-options":{DontEstimate:"Non stimare",EstimateFromSunHours:"Stima dalle ore solari",EstimateFromTemp:"Stima dalla temperatura",EstimateFromSunHoursAndTemperature:"Stima dalla media delle ore di sole e della temperatura"}}},description:"Aggiungi uno o più moduli che calcolano la durata dell'irrigazione. Ogni modulo viene fornito con la propria configurazione e può essere utilizzato per calcolare la durata di una o più zone.",no_items:"Non ci sono ancora moduli definiti.",title:"Moduli"},zones:{actions:{add:"Aggiungi",calculate:"Calcola",information:"Informazioni",update:"Aggiorna","reset-bucket":"Reimposta il secchio","view-weather-info":"Visualizza dati meteo","view-weather-info-message":"Informazioni meteo disponibili per","view-weather-info-todo":"TODO: Implementare la navigazione ai dettagli del gruppo di sensori","view-watering-calendar":"Calendario irrigazione",irrigate_all:"Esegui tutte le zone ora"},cards:{"add-zone":{actions:{add:"Aggiungi zona"},header:"Aggiungi zona"},"zone-actions":{actions:{"calculate-all":"Calcola tutte le zone","update-all":"Aggiorna tutte le zone","reset-all-buckets":"Reimposta tutte le zone","clear-all-weatherdata":"Cancella tutti i dati meteo"},header:"Azioni su tutte le zone"}},description:"Specificare qui una o più zone di irrigazione. La durata dell'irrigazione viene calcolata per zona, a seconda delle dimensioni, della produttività, dello stato, del modulo e del gruppo di sensori.",labels:{bucket:"Secchio",duration:"Durata","lead-time":"Tempi di esecuzione",mapping:"Gruppo di sensori","maximum-duration":"Durata massima",multiplier:"Moltiplicatore",name:"Nome",size:"Misura",state:"Stato",states:{automatic:"Automatico",disabled:"Disabilitato",manual:"Manuale"},throughput:"Portata","maximum-bucket":"Secchio massimo",last_calculated:"Ultimo calcolo","data-last-updated":"Ultimo aggiornamento dei dati","data-number-of-data-points":"Numero di dati",tasso_di_drenaggio:"tasso di drenaggio",drainage_rate:"Tasso di drenaggio",linked_entity:"Entità interruttore/valvola collegata",linked_entity_placeholder:"es. switch.valvola_giardino",irrigate_now:"Irriga ora",bucket_threshold:"Deficit minimo per irrigare",flow_sensor:"Sensore del flussometro (opzionale)",flow_sensor_placeholder:"ad es. sensor.zone_flow_rate"},no_items:"Non ci sono ancora zone definite.",title:"Zone",confirm_irrigate:{title:"Avviare l'irrigazione?",body:"Verranno aperte ora le valvole collegate, ignorando tutte le condizioni di esclusione (pioggia, temperatura, giorni minimi tra le irrigazioni).",all_linked_zones:"Tutte le zone collegate",toast_started:"Irrigazione avviata",toast_failed:"Irrigazione non riuscita"}},schedules:{title:"Pianificazioni",description:"Crea pianificazioni ricorrenti per calcolare, aggiornare o irrigare automaticamente — senza automazioni.",add:"Aggiungi pianificazione",no_items:"Nessuna pianificazione configurata. Fare clic su 'Aggiungi pianificazione'.",zones_all:"Tutte le zone",zones_specific:"Zone specifiche",hours:"ore",minutes:"min",types:{daily:"Giornaliero",weekly:"Settimanale",monthly:"Mensile",interval:"Ogni N ore",sunrise:"Alba",sunset:"Tramonto",solar_azimuth:"Azimut solare"},actions:{calculate:"Calcola (aggiorna durata irrigazione)",update:"Aggiorna (raccogliere dati meteo)",irrigate:"Irriga (controllare valvole direttamente)"},days:{monday:"Lu",tuesday:"Ma",wednesday:"Me",thursday:"Gi",friday:"Ve",saturday:"Sa",sunday:"Do"},fields:{name:"Nome",type:"Tipo di pianificazione",enabled:"Abilitato",time:"Ora (HH:MM)",days_of_week:"Giorni della settimana",day_of_month:"Giorno del mese",interval_hours:"Intervallo",action:"Azione",zones:"Zone",start_date:"Data di inizio (opzionale)",end_date:"Data di fine (opzionale)",offset_minutes:"Offset dall'alba/tramonto",account_for_duration:"Iniziare prima affinché l'irrigazione finisca all'orario target",azimuth_angle:"Angolo di azimut solare"},dialog:{add_title:"Aggiungi pianificazione",edit_title:"Modifica pianificazione"}},setup:{title:"Configurazione"}},Ja="Smart Irrigation",Qa={title:"Coordinate di Posizione",description:"Configura le coordinate di posizione per il recupero dei dati meteorologici. Puoi usare coordinate manuali diverse dalla tua posizione Home Assistant se necessario.",manual_enabled:"Usa coordinate manuali",use_ha_location:"Usa posizione di Home Assistant",latitude:"Latitudine (gradi decimali)",longitude:"Longitudine (gradi decimali)",elevation:"Elevazione (metri sul livello del mare)",current_ha_coords:"Coordinate attuali di Home Assistant"},ei={title:"Giorni tra irrigazioni",description:"Configura il numero minimo di giorni tra gli eventi di irrigazione.",label:"Giorni minimi tra irrigazioni",help_text:"Impostare 0 per disabilitare. Sono supportati valori da 1 a 365 giorni."},ti={title:"Trigger di avvio irrigazione",description:"Configura quando deve iniziare l'irrigazione in base agli eventi solari. Puoi aggiungere più trigger per orari diversi. Per i trigger all'alba, lasciando lo scostamento a 0 verrà usata automaticamente la durata totale di tutte le zone abilitate.",add_trigger:"Aggiungi trigger",edit_trigger:"Modifica trigger",delete_trigger:"Elimina trigger",trigger_types:{sunrise:"Alba",sunset:"Tramonto",solar_azimuth:"Azimut solare"},fields:{name:{name:"Nome del trigger",description:"Un nome descrittivo per identificare questo trigger"},type:{name:"Tipo di trigger",description:"Il tipo di evento solare su cui attivare"},enabled:{name:"Abilitato",description:"Se questo trigger è attualmente attivo"},offset_minutes:{name:"Scostamento (minuti)",description:"Minuti prima (-) o dopo (+) l'evento solare. Per i trigger all'alba, usa 0 per una temporizzazione automatica basata sulla durata totale delle zone."},azimuth_angle:{name:"Angolo di azimut (gradi)",description:"Angolo di azimut solare in gradi dove 0=Nord, 90=Est, 180=Sud, 270=Ovest"},account_for_duration:{name:"Considera la durata",description:"Se abilitato, l'irrigazione inizierà abbastanza presto da terminare all'ora specificata. Se disabilitato, l'irrigazione inizierà esattamente all'ora specificata."}},dialog:{add_title:"Aggiungi trigger di avvio irrigazione",edit_title:"Modifica trigger di avvio irrigazione",cancel:"Annulla",save:"Salva",delete:"Elimina"},no_triggers:"Nessun trigger di avvio irrigazione configurato. Il sistema userà il comportamento predefinito (alba con la durata totale delle zone). Aggiungi trigger per personalizzare l'avvio dell'irrigazione.",offset_auto:"Automatico (calcolato dalla durata totale delle zone)",confirm_delete:"Vuoi davvero eliminare il trigger '{name}'?",validation:{name_required:"Il nome del trigger è obbligatorio",azimuth_invalid:"L'angolo di azimut deve essere un numero valido"},help:{sunrise_offset:"Per i trigger all'alba: usa valori negativi per iniziare prima dell'alba, positivi per iniziare dopo. Imposta 0 per iniziare automaticamente con abbastanza anticipo da completare tutte le zone prima dell'alba.",sunset_offset:"Per i trigger al tramonto: usa valori negativi per iniziare prima del tramonto, positivi per iniziare dopo il tramonto.",azimuth_explanation:"L'azimut solare è la direzione bussolare del sole. 0°=Nord, 90°=Est, 180°=Sud, 270°=Ovest. Puoi inserire qualsiasi valore di angolo (ad es. 450° = 90°, -30° = 330°). Usalo per attivare l'irrigazione quando il sole raggiunge una posizione specifica.",multiple_triggers:"Puoi configurare più trigger. Ogni trigger abilitato pianificherà gli avvii dell'irrigazione in modo indipendente."}},ai={title:"Condizioni di esclusione",description:"Salta automaticamente l'irrigazione quando le condizioni sono sfavorevoli. I controlli di precipitazioni, temperatura e vento richiedono un servizio meteo.",threshold_label:"Soglia di precipitazioni",threshold_description:"Quantità minima di precipitazioni previste (in mm) per oggi e domani per saltare l'irrigazione.",temp_section_title:"Salta per bassa temperatura",temp_threshold_label:"Salta se temperatura sotto",wind_section_title:"Salta per vento forte",wind_threshold_label:"Salta se velocità del vento superiore a",rain_sensor_section_title:"Condizione sensore pioggia",rain_sensor_label:"Entità sensore pioggia (opzionale)",rain_sensor_placeholder:"es. binary_sensor.pioggia"},ii={title:"Sequenza zone",description:"Quando più zone necessitano di irrigazione, scegliere se funzionano contemporaneamente o una dopo l'altra. In modalità sequenziale, il sistema attende che ogni zona finisca prima di avviare la successiva. In modalità rotante, il sistema alterna tra le zone assegnando a ciascuna un tempo massimo consecutivo prima di passare alla successiva.",parallel:"Parallelo (tutte le zone insieme)",sequential:"Sequenziale (una zona alla volta)",rotating:"Rotante (le zone si alternano)",max_consecutive_duration_label:"Tempo massimo consecutivo per zona",max_consecutive_duration_unit:"minuti",min_absorption_time_label:"Tempo minimo di assorbimento tra slot",min_absorption_time_unit:"minuti (0 = disabilitato)"},ni={title:"Servizio meteo",description:"Configura quale servizio meteo usare per i calcoli ET e le condizioni di salto.",enabled_label:"Abilita servizio meteo",service_label:"Servizio meteo",api_key_label:"Chiave API",api_key_placeholder:"Lascia vuoto per mantenere la chiave esistente",api_key_configured:"La chiave API è configurata",api_key_not_configured:"Nessuna chiave API configurata",api_key_help:"Una chiave API del provider di servizio meteo scelto. Open-Meteo non richiede una chiave. OpenWeatherMap e Pirate Weather offrono entrambi piani gratuiti.",no_api_key_needed:"Open-Meteo è un servizio gratuito e non richiede una chiave API.",save_button:"Salva impostazioni meteo",saved:"Impostazioni meteo salvate",openmeteo:"Open-Meteo (gratuito, senza chiave)",test_button:"Prova connessione",test_button_testing:"Test in corso…",test_success:"✓ Connessione riuscita",test_error_invalid_auth:"✗ Chiave API non valida — verifica che sia corretta e attiva",test_error_cannot_connect:"✗ Impossibile connettersi — controlla la connessione internet",test_error_no_service:"✗ Seleziona prima un servizio meteo",test_error_unknown:"✗ Test fallito — errore sconosciuto",owm:"OpenWeatherMap",pw:"Pirate Weather"},si={zone_size:"L'area irrigata totale di questa zona. Usata con la portata per calcolare quanta acqua viene erogata per ciclo.",zone_throughput:"Flusso d'acqua totale del tuo impianto di irrigazione per questa zona (litri/min in metrico, gal/min in imperiale). Controlla la scheda tecnica degli irrigatori o misura cronometrando quanto tempo serve a riempire un contenitore di volume noto.",zone_drainage_rate:"La velocità con cui l'acqua in eccesso drena dal terreno quando il secchio è pieno. Tipico: prato 50 mm/h, terreno sabbioso 100+ mm/h, argilla 10 mm/h.",zone_bucket:"Deficit (negativo) o surplus (positivo) idrico attuale di questa zona. L'irrigazione si attiva quando il secchio scende sotto la soglia.",zone_maximum_bucket:"Surplus di umidità massimo che la zona può trattenere. L'acqua oltre questo livello è trattata come deflusso. Valore tipico: 50 mm.",zone_bucket_threshold:"L'irrigazione si attiva quando il secchio scende sotto questo valore. Deve essere 0 o negativo. 0 significa irrigare ogni volta che c'è un deficit.",zone_multiplier:"Fattore di scala applicato alla durata calcolata. Sopra 1,0 aumenta, sotto 1,0 diminuisce. Utile per la messa a punto senza modificare le misure fisiche.",zone_lead_time:"Secondi aggiuntivi prima dell'avvio dell'irrigazione. Usali per il riscaldamento della pompa o la pressurizzazione dell'impianto.",zone_maximum_duration:"Limite massimo assoluto per un singolo ciclo di irrigazione in secondi. Previene irrigazioni incontrollate. Predefinito: 3600 s (1 ora).",zone_linked_entity:"L'entità interruttore o valvola di HA che controlla il flusso d'acqua per questa zona. Questa entità viene attivata quando l'irrigazione è in funzione.",zone_flow_sensor:"Sensore opzionale che misura la portata d'acqua effettiva. Usato solo per i report — non influisce sul calcolo della durata.",general_autoupdatedelay:"Secondi di attesa dopo l'avvio di HA prima del primo recupero dei dati meteo. Consente alle altre integrazioni di inizializzarsi prima.",general_sensor_debounce:"Intervallo minimo in millisecondi tra le letture del sensore per filtrare il rumore dei sensori che cambiano rapidamente.",general_calctime:"Ora del giorno in cui le durate di irrigazione vengono ricalcolate dai dati meteo raccolti. Formato: HH:MM (24 ore).",general_cleardatatime:"Ora del giorno in cui i vecchi dati meteo vengono eliminati. Deve essere impostata dopo l'ora di calcolo.",general_days_between:"Giorni minimi tra gli eventi di irrigazione per la stessa zona. Imposta 0 per disabilitare (irrigare ogni volta che c'è un deficit).",general_autoupdateinterval:"Con quale frequenza vengono raccolti i dati meteo. Scegli un valore che bilanci dati aggiornati e limiti dell'API.",general_precipitation_threshold:"L'irrigazione viene saltata se le precipitazioni previste per oggi/domani superano questa quantità.",general_temp_threshold:"L'irrigazione viene saltata se la temperatura attuale è inferiore a questo valore (ad es. per prevenire danni da gelo).",general_wind_threshold:"L'irrigazione viene saltata se la velocità del vento supera questo valore (il vento forte riduce l'efficienza e causa deriva)."},ri={title:"Configurazione guidata",open_button:"Configurazione guidata",close:"Chiudi",next:"Avanti",back:"Indietro",finish:"Fine",skip_step:"Salta questo passaggio",step_indicator:"Passaggio {current} di {total}",setup_complete_banner:"Configurazione non completata. Avvia la procedura guidata per iniziare.",open_wizard:"Apri procedura guidata",steps:{welcome:{title:"Benvenuto in Smart Irrigation",intro:"Questa procedura guidata ti accompagna nei quattro passaggi necessari per far irrigare automaticamente la tua prima zona.",step1_label:"Servizio meteo — dove ottenere i dati meteo",step2_label:"Modulo di calcolo — come viene calcolata la durata dell'irrigazione",step3_label:"Gruppo di sensori — quali fonti di dati usare",step4_label:"Zona — la tua prima zona di irrigazione",tip:"Puoi saltare qualsiasi passaggio e configurarlo in seguito dalla scheda Configurazione."},weather:{title:"Servizio meteo",description:"Scegli come ottenere i dati meteo. Open-Meteo è gratuito e non richiede una chiave API — è la scelta più semplice per la maggior parte degli utenti."},module:{title:"Modulo di calcolo",description:"Un modulo calcola quanto irrigare in base all'evapotraspirazione (ET). Il modulo PyETO (metodo FAO-56) è consigliato per la maggior parte degli utenti.",pick_label:"Seleziona il tipo di modulo",no_modules:"Nessun tipo di modulo disponibile."},mapping:{title:"Gruppo di sensori",description:"Un gruppo di sensori collega ogni variabile meteo a una fonte di dati. Imposta le variabili chiave qui sotto — potrai perfezionare le singole associazioni dei sensori in seguito dalla scheda Configurazione → Gruppi di sensori.",name_label:"Nome del gruppo di sensori",source_label:"Fonte di dati per",use_weather_service:"Servizio meteo",use_sensor:"Sensore",use_static:"Valore statico",use_none:"Nessuna / non usata"},zone:{title:"Prima zona",description:"Una zona è un'area di irrigazione (ad es. prato, aiuola). Imposta le proprietà fisiche affinché il sistema possa calcolare la durata di irrigazione corretta.",name_label:"Nome della zona",size_label:"Area",throughput_label:"Portata dell'irrigatore",entity_label:"Interruttore o valvola collegati",entity_placeholder:"ad es. switch.garden_valve",module_label:"Modulo di calcolo",mapping_label:"Gruppo di sensori"},done:{title:"Configurazione completata!",description:"La tua prima zona è pronta. Smart Irrigation calcolerà ora le durate di irrigazione automaticamente in base ai dati meteo.",next_steps:"Cosa puoi fare ora:",tip1:"Vai su Zone per vedere le durate calcolate e i valori del secchio.",tip2:"Aggiungi altre zone dalla scheda Zone.",tip3:"Perfeziona tutte le impostazioni dalla scheda Configurazione.",go_zones:"Vai a Zone",go_setup:"Vai a Configurazione"}}},oi={common:Za,defaults:Ya,module:Ga,calcmodules:Ka,panels:Xa,title:Ja,coordinate_config:Qa,days_between_irrigation:ei,irrigation_start_triggers:ti,weather_skip:ai,zone_sequencing:ii,weather_service_config:ni,field_help:si,wizard:ri},li=Object.freeze({__proto__:null,common:Za,defaults:Ya,module:Ga,calcmodules:Ka,panels:Xa,title:Ja,coordinate_config:Qa,days_between_irrigation:ei,irrigation_start_triggers:ti,weather_skip:ai,zone_sequencing:ii,weather_service_config:ni,field_help:si,wizard:ri,default:oi}),di={actions:{delete:"Verwijderen",edit:"Bewerken",save:"Opslaan",cancel:"Annuleren",confirm_delete:"Verwijderen bevestigen",confirm_delete_zone:"Weet je zeker dat je deze zone wilt verwijderen?"},labels:{module:"Module",no:"Nee",select:"Kies",yes:"Ja",enabled:"Ingeschakeld",disabled:"Uitgeschakeld",before:"voor",after:"na",settings:"Instellingen",bulk_actions:"Bulkacties"},attributes:{size:"afmeting",throughput:"doorvoer",state:"status",bucket:"emmer",last_updated:"laatste update",last_calculated:"laatste berekening",number_of_data_points:"aantal datapunten"},loading:"Laden",saving:"Opslaan",units:{seconds:"seconden"},"loading-messages":{configuration:"Configuratie laden...",modules:"Modules laden...",general:"Laden..."},"saving-messages":{adding:"Toevoegen...",saving:"Opslaan..."},errors:{load_failed:"Kan gegevens niet laden",save_failed:"Kan wijzigingen niet opslaan",delete_failed:"Kan niet verwijderen",action_failed:"Actie mislukt"}},ui={"default-zone":"Standaard zone","default-mapping":"Standaard sensorgroep"},ci={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"NB: in deze uitleg wordt de '.' as decimaalscheidingsteken gebruikt, worden afgeronde en metrische getallen getoond. Module berekende ET waarde van","bucket-was":"Voorraad was","new-bucket-values-is":"Nieuwe voorraad is","old-bucket-variable":"oude_voorraad",delta:"verandering","bucket-less-than-zero-irrigation-necessary":"Omdat de voorraad < 0 is, is irrigatie nodig","steps-taken-to-calculate-duration":"On de exacte duur te berekenen werd het volgende gedaan","precipitation-rate-defined-as":"De neerslag is","duration-is-calculated-as":"De duur is",bucket:"voorraad","precipitation-rate-variable":"neerslag","multiplier-is-applied":"De vermenigvuldiger wordt toegepast. Deze is","duration-after-multiplier-is":"dus de duur is","maximum-duration-is-applied":"De maximum duur wordt toegepast. Deze is","duration-after-maximum-duration-is":"dus de duur is","lead-time-is-applied":"As laatste wordt de aanlooptijd toegepast. Deze is","duration-after-lead-time-is":"dus de uiteindelijke duur is","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Omdat de voorraad >= 0 is er geen irrigatie nodig en is de duur gelijk aan","maximum-bucket-is":"maximale voorraad grootte is","max-bucket-variable":"max_bucket",drainage:"afwatering","drainage-rate":"afwateringssnelheid",hours:"uren","drainage-rate-is":"Drainagesnelheid bij verzadiging (emmer op maximum) is","current-drainage-is":"Huidige drainage berekend als","no-drainage":"Huidige drainage is 0 omdat"}}},pi={pyeto:{description:"Bereken duur op basis van de FAU56 formule en de PyETO library"},static:{description:"Module met instelbare verandering"},passthrough:{description:"Geeft waarde van ET sensor as verandering terug"}},hi={general:{cards:{"automatic-duration-calculation":{header:"Automatische berekening van irrigatietijd",description:"Bij het berekenen wordt de verzamelde weersinformatie gebruikt om the voorraad en irrigatieduur per zone aan te passen. Daarna wordt de verzamelde weersinformatie verwijderd.",labels:{"auto-calc-enabled":"Automatisch irrigatietijd berekening voor elke zone","auto-calc-time":"Berekenen op","calc-time":"Berekenen om"}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Let op: het automatisch bijwerken van weersinformatie vind plaats op of na de automatische berekening van irrigatietijd"},header:"Automatisch bijwerken van weersinformatie",description:"Verzamel en bewaar weersinformatie automatisch. Weersinformatie is nodig om vorraad en irrigatieduur per zone te berekenen.",labels:{"auto-update-enabled":"Automatisch weersinformatie bijwerken","auto-update-delay":"Vertraging","auto-update-interval":"Sensor data bijwerken elke","auto-update-schedule":"Updateschema","auto-update-time":"Bijwerken om"},options:{days:"dagen",hours:"uren",minutes:"minuten"}},"automatic-clear":{header:"Automatisch weersinformatie opruimen",description:"Verwijder weersinformatie op het ingestelde moment. Dit zorgt ervoor dat er geen weersinformatie van de vorige dag gebruikt kan worden voor berekeningen. Let op: verwijder geen weersinformatie voordat de berekening heeft plaatsgevonden. Gebruik deze optie als je verwacht dat er weersinformatie zal worden verzameld nadat de berekeningen voor de dag gedaan zijn. Verwijder weersinformatie zo laat mogelijk op de dag.",labels:{"automatic-clear-enabled":"Automatisch weersinformatie verwijderen","automatic-clear-time":"Verwijder weersinformatie om"}},continuousupdates:{header:"Continue sensorupdates (experimenteel)",description:"Experimentele functie voor gedetailleerdere weergegevens.",labels:{continuousupdates:"Continue updates inschakelen",sensor_debounce:"Sensor-debounce","sensor-debounce":"Sensor-debouncetijd (ms)"}}},description:"Dit zijn de algemene instellingen.",title:"Algemeen"},help:{title:"Hulp",cards:{"how-to-get-help":{title:"Hulp vragen","first-read-the":"Allereerst, lees de",wiki:"Documentatie","if-you-still-need-help":"Als je hierna nog steeds hulp nodig hebt, laat een bericht achter op het","community-forum":"Communityforum","or-open-a":"of open een","github-issue":"GitHub-issue","english-only":"alleen Engels"}}},mappings:{cards:{"add-mapping":{actions:{add:"Toevoegen"},header:"Voeg sensorgroep toe"},mapping:{aggregates:{average:"Gemiddelde",first:"Eerste",last:"Laatste",maximum:"Maximum",median:"Mediaan",minimum:"Minimum",sum:"Totaal",riemannsum:"Riemann-som",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"Deze sensorgroep kan niet worden verwijderd omdat er minimaal een zone gebruik van maakt.",invalid_source:"Ongeldige bron",source_does_not_exist:"Bron bestaat niet. Voer een geldige bron in, zoals 'sensor.mysensor'."},items:{dewpoint:"Dauwpunt",evapotranspiration:"Verdamping",humidity:"Vochtigheid","maximum temperature":"Maximum temperatuur","minimum temperature":"Minimum temperatuur",precipitation:"Totale neerslag",pressure:"Druk","solar radiation":"Zonnestraling",temperature:"Temperatuur",windspeed:"Wind snelheid","current precipitation":"Huidige neerslag"},pressure_types:{absolute:"absoluut",relative:"relatief"},"pressure-type":"Druk is","sensor-aggregate-of-sensor-values-to-calculate":"van de sensor waardes om irrigatietijd te berekenen","sensor-aggregate-use-the":"Gebruik de/het","sensor-entity":"Sensor entiteit","input-units":"Invoer geeft waardes in",static_value:"Waarde",source:"Bron",sources:{none:"Geen",weather_service:"Weerdienst",sensor:"Sensor",static:"Vaste waarde"}}},description:"Voeg een of meer sensorgroepen toe die weergegevens ophalen van Weather service, van sensoren of een combinatie. Elke sensorgroep kan worden gebruikt voor een of meerdere zones",labels:{"mapping-name":"Naam"},no_items:"Er zijn nog geen sensorgroepen.",title:"Sensorgroepen","weather-records":{title:"Weerregistraties",timestamp:"Tijd",temperature:"Temp.",humidity:"Humidity",precipitation:"Neersl.","retrieval-time":"Opgehaald","no-data":"Geen weergegevens beschikbaar voor deze sensorgroep",dewpoint:"Dauw",wind:"Wind",pressure:"Druk"}},modules:{cards:{"add-module":{actions:{add:"Toevoegen"},header:"Voeg module toe"},module:{errors:{"cannot-delete-module-because-zones-use-it":"Deze module kan niet worden verwijderd omdat er minimaal een zone gebruik van maakt."},labels:{configuration:"Instellingen",required:"verplicht veld"},"translated-options":{DontEstimate:"Niet berekenen",EstimateFromSunHours:"Gebaseerd op zon uren",EstimateFromTemp:"Gebaseerd op temperatuur",EstimateFromSunHoursAndTemperature:"Schatten op basis van het gemiddelde van zonuren en temperatuur"}}},description:"Voeg een of meerdere modules toe. Modules berekenen irrigatietijd. Elke module heeft zijn eigen configuratie and kan worden gebruikt voor het berekening van irrigatietijd voor een of meerdere zones.",no_items:"Er zijn nog geen modules.",title:"Modules"},zones:{actions:{add:"Toevoegen",calculate:"Bereken",information:"Informatie",update:"Bijwerken","reset-bucket":"Leeg voorraad","view-weather-info":"Weergegevens bekijken","view-weather-info-message":"Weergegevens beschikbaar voor","view-watering-calendar":"Bewateringskalender",irrigate_all:"Alle zones nu uitvoeren"},cards:{"add-zone":{actions:{add:"Toevoegen"},header:"Voeg zone toe"},"zone-actions":{actions:{"calculate-all":"Bereken alle zones","update-all":"Werk alle zone data bij","reset-all-buckets":"Leeg alle voorraden","clear-all-weatherdata":"Verwijder alle weersinformatie"},header:"Acties voor alle zones"}},description:"Voeg een of meerdere zones toe. Per zone wordt de irrigatietijd berekend, afhankelijk van de afmeting, doorvoer, status, module en sensorgroep.",labels:{bucket:"Voorraad",duration:"Irrigatieduur","lead-time":"Aanlooptijd",mapping:"Sensorgroep","maximum-duration":"Maximale duur",multiplier:"Vermenigvuldiger",name:"Naam",size:"Afmeting",state:"Status",states:{automatic:"Automatisch",disabled:"Uit",manual:"Manueel"},throughput:"Doorvoer","maximum-bucket":"Maximale voorraad",last_calculated:"Berekend op","data-last-updated":"Bijgewerkt op","data-number-of-data-points":"Aantal datapunten",drainage_rate:"Afwateringssnelheid",linked_entity:"Gekoppelde schakelaar/klep-entiteit",linked_entity_placeholder:"bijv. switch.tuin_klep",irrigate_now:"Nu bewateren",bucket_threshold:"Minimum tekort voor bewatering",flow_sensor:"Doorstroommeter-sensor (optioneel)",flow_sensor_placeholder:"bijv. sensor.zone_flow_rate"},no_items:"Er zijn nog geen zones.",title:"Zones",confirm_irrigate:{title:"Irrigatie starten?",body:"Dit opent nu de gekoppelde klep(pen) en negeert alle uitsluitingsvoorwaarden (regen, temperatuur, minimaal aantal dagen tussen beurten).",all_linked_zones:"Alle gekoppelde zones",toast_started:"Irrigatie gestart",toast_failed:"Irrigatie mislukt"}},schedules:{title:"Schema's",description:"Maak terugkerende schema's voor automatisch berekenen, bijwerken of bewateren — zonder automatiseringen.",add:"Schema toevoegen",no_items:"Nog geen schema's geconfigureerd. Klik op 'Schema toevoegen'.",zones_all:"Alle zones",zones_specific:"Specifieke zones",hours:"uur",minutes:"min",types:{daily:"Dagelijks",weekly:"Wekelijks",monthly:"Maandelijks",interval:"Elke N uur",sunrise:"Zonsopgang",sunset:"Zonsondergang",solar_azimuth:"Zonneazimut"},actions:{calculate:"Berekenen (bewateringsduur bijwerken)",update:"Bijwerken (weergegevens verzamelen)",irrigate:"Bewateren (kleppen direct aansturen)"},days:{monday:"Ma",tuesday:"Di",wednesday:"Wo",thursday:"Do",friday:"Vr",saturday:"Za",sunday:"Zo"},fields:{name:"Naam",type:"Schematype",enabled:"Ingeschakeld",time:"Tijd (HH:MM)",days_of_week:"Weekdagen",day_of_month:"Dag van de maand",interval_hours:"Interval",action:"Actie",zones:"Zones",start_date:"Startdatum (optioneel)",end_date:"Einddatum (optioneel)",offset_minutes:"Offset van zonsopgang/-ondergang",account_for_duration:"Vroeg starten zodat bewatering eindigt op doeltijd",azimuth_angle:"Zonneazimuthoek"},dialog:{add_title:"Schema toevoegen",edit_title:"Schema bewerken"}},info:{title:"Info",description:"Informatie bekijken over de volgende bewatering en systeemstatus.","configuration-not-available":"Configuratie niet beschikbaar.",cards:{"zone-bucket-values":{title:"Zone-emmerwaarden & duur",labels:{bucket:"Emmer",duration:"Duur"},"no-zones":"Geen zones geconfigureerd"},"next-irrigation":{title:"Volgende bewatering",labels:{"next-start":"Volgende start",duration:"Duur",zones:"Zones"},"no-data":"Geen gegevens beschikbaar"},"irrigation-reason":{title:"Reden voor bewatering",labels:{reason:"Reden",sunrise:"Zonsopgang","total-duration":"Totale duur",explanation:"Uitleg"},"no-data":"Geen gegevens beschikbaar"},irrigate_now:{title:"Nu bewateren",description:"Start direct bewatering voor alle zones met een gekoppelde entiteit. Overslaanvoorwaarden worden genegeerd.",button_all:"Alle zones nu starten",no_linked_zones:"Geen zones hebben een gekoppelde schakelaar/klep-entiteit met berekende duur."}}},setup:{title:"Instellen"}},gi="Smart Irrigation",mi={title:"Locatie Coördinaten",description:"Configureer locatie coördinaten voor het ophalen van weergegevens. Je kunt handmatige coördinaten gebruiken die verschillen van je Home Assistant locatie indien nodig.",manual_enabled:"Handmatige coördinaten gebruiken",use_ha_location:"Home Assistant locatie gebruiken",latitude:"Breedtegraad (decimale graden)",longitude:"Lengtegraad (decimale graden)",elevation:"Hoogte (meters boven zeeniveau)",current_ha_coords:"Huidige Home Assistant coördinaten"},vi={title:"Dagen tussen bewatering",description:"Stel het minimum aantal dagen in tussen bewateringsgebeurtenissen.",label:"Minimum dagen tussen bewatering",help_text:"Stel in op 0 om uit te schakelen. Waarden van 1-365 dagen worden ondersteund."},fi={title:"Irrigatiestart-triggers",description:"Configureer wanneer de irrigatie moet starten op basis van zonne-evenementen. Je kunt meerdere triggers toevoegen voor verschillende schema's. Voor zonsopkomst-triggers gebruikt een offset van 0 automatisch de totale duur van alle ingeschakelde zones.",add_trigger:"Trigger toevoegen",edit_trigger:"Trigger bewerken",delete_trigger:"Trigger verwijderen",trigger_types:{sunrise:"Zonsopkomst",sunset:"Zonsondergang",solar_azimuth:"Zonsazimut"},fields:{name:{name:"Triggernaam",description:"Een beschrijvende naam om deze trigger te identificeren"},type:{name:"Triggertype",description:"Het type zonne-evenement om op te triggeren"},enabled:{name:"Ingeschakeld",description:"Of deze trigger momenteel actief is"},offset_minutes:{name:"Offset (minuten)",description:"Minuten voor (-) of na (+) het zonne-evenement. Gebruik voor zonsopkomst-triggers 0 voor automatische timing op basis van de totale zoneduur."},azimuth_angle:{name:"Azimuthoek (graden)",description:"Zonsazimuthoek in graden waarbij 0=Noord, 90=Oost, 180=Zuid, 270=West"},account_for_duration:{name:"Rekening houden met duur",description:"Indien ingeschakeld start de irrigatie vroeg genoeg om op het opgegeven tijdstip klaar te zijn. Indien uitgeschakeld start de irrigatie precies op het opgegeven tijdstip."}},dialog:{add_title:"Irrigatiestart-trigger toevoegen",edit_title:"Irrigatiestart-trigger bewerken",cancel:"Annuleren",save:"Opslaan",delete:"Verwijderen"},no_triggers:"Geen irrigatiestart-triggers geconfigureerd. Het systeem gebruikt het standaardgedrag (zonsopkomst met de totale zoneduur). Voeg triggers toe om aan te passen wanneer de irrigatie start.",offset_auto:"Automatisch (berekend uit de totale zoneduur)",confirm_delete:"Weet je zeker dat je de trigger '{name}' wilt verwijderen?",validation:{name_required:"Triggernaam is verplicht",azimuth_invalid:"De azimuthoek moet een geldig getal zijn"},help:{sunrise_offset:"Voor zonsopkomst-triggers: gebruik negatieve waarden om vóór zonsopkomst te starten, positieve om erna te starten. Zet op 0 om automatisch vroeg genoeg te starten om alle zones vóór zonsopkomst te voltooien.",sunset_offset:"Voor zonsondergang-triggers: gebruik negatieve waarden om vóór zonsondergang te starten, positieve om na zonsondergang te starten.",azimuth_explanation:"De zonsazimut is de kompasrichting van de zon. 0°=Noord, 90°=Oost, 180°=Zuid, 270°=West. Je kunt elke hoekwaarde invoeren (bijv. 450° = 90°, -30° = 330°). Gebruik dit om de irrigatie te triggeren wanneer de zon een specifieke positie bereikt.",multiple_triggers:"Je kunt meerdere triggers configureren. Elke ingeschakelde trigger plant irrigatiestarts onafhankelijk."}},_i={title:"Overslaanvoorwaarden",description:"Sla irrigatie automatisch over als de omstandigheden ongunstig zijn. Neerslag-, temperatuur- en windcontroles vereisen een weerdienst.",threshold_label:"Neerslagdrempel",threshold_description:"Minimale hoeveelheid verwachte neerslag (in mm) voor vandaag en morgen om irrigatie over te slaan.",temp_section_title:"Overslaan bij lage temperatuur",temp_threshold_label:"Overslaan als temperatuur onder",wind_section_title:"Overslaan bij hoge windsnelheid",wind_threshold_label:"Overslaan als windsnelheid boven",rain_sensor_section_title:"Regensensorvoorwaarde",rain_sensor_label:"Regensensor-entiteit (optioneel)",rain_sensor_placeholder:"bijv. binary_sensor.regen"},bi={title:"Zone-volgorde",description:"Als meerdere zones irrigatie nodig hebben, kies of ze tegelijkertijd of na elkaar worden uitgevoerd. In sequentiële modus wacht het systeem tot elke zone klaar is voordat de volgende start.",parallel:"Parallel (alle zones tegelijk)",sequential:"Sequentieel (één zone tegelijk)",rotating:"Roterend (zones wisselen elkaar af)",max_consecutive_duration_label:"Max. aaneengesloten looptijd per zone",max_consecutive_duration_unit:"minuten",min_absorption_time_label:"Min. absorptietijd tussen runs",min_absorption_time_unit:"minuten (0 = uitgeschakeld)"},yi={title:"Weerdienst",description:"Configureer welke weerdienst gebruikt wordt voor ET-berekeningen en overslaan-voorwaarden.",enabled_label:"Weerdienst inschakelen",service_label:"Weerdienst",api_key_label:"API-sleutel",api_key_placeholder:"Laat leeg om de bestaande sleutel te behouden",api_key_configured:"API-sleutel is geconfigureerd",api_key_not_configured:"Geen API-sleutel geconfigureerd",api_key_help:"Een API-sleutel van je gekozen weerdienstaanbieder. Open-Meteo vereist geen sleutel. OpenWeatherMap en Pirate Weather bieden beide gratis niveaus.",no_api_key_needed:"Open-Meteo is een gratis dienst en vereist geen API-sleutel.",save_button:"Weerinstellingen opslaan",saved:"Weerinstellingen opgeslagen",openmeteo:"Open-Meteo (gratis, geen sleutel nodig)",test_button:"Verbinding testen",test_button_testing:"Bezig met testen…",test_success:"✓ Verbinding geslaagd",test_error_invalid_auth:"✗ Ongeldige API-sleutel — controleer of deze correct en actief is",test_error_cannot_connect:"✗ Kan geen verbinding maken — controleer je internetverbinding",test_error_no_service:"✗ Selecteer eerst een weerdienst",test_error_unknown:"✗ Test mislukt — onbekende fout",owm:"OpenWeatherMap",pw:"Pirate Weather"},wi={zone_size:"Het totale geïrrigeerde oppervlak van deze zone. Wordt samen met de doorvoer gebruikt om te berekenen hoeveel water per run wordt toegediend.",zone_throughput:"Totale waterstroom van je irrigatiesysteem voor deze zone (liter/min in metriek, gal/min in imperiaal). Raadpleeg het gegevensblad van je sproeiers of meet hoe lang het duurt om een bak met bekende inhoud te vullen.",zone_drainage_rate:"Hoe snel overtollig water uit de bodem wegloopt als de emmer vol is. Typisch: gazon 50 mm/u, zandgrond 100+ mm/u, klei 10 mm/u.",zone_bucket:"Huidig watertekort (negatief) of -overschot (positief) voor deze zone. Irrigatie wordt geactiveerd wanneer de emmer onder de drempel zakt.",zone_maximum_bucket:"Maximaal vochtoverschot dat de zone kan vasthouden. Water boven dit niveau wordt als afstroming behandeld. Typische waarde: 50 mm.",zone_bucket_threshold:"Irrigatie wordt geactiveerd wanneer de emmer onder deze waarde zakt. Moet 0 of negatief zijn. 0 betekent irrigeren zodra er een tekort is.",zone_multiplier:"Schaalfactor toegepast op de berekende duur. Boven 1,0 verhoogt, onder 1,0 verlaagt. Handig voor fijnafstemming zonder fysieke metingen te wijzigen.",zone_lead_time:"Extra seconden voordat de irrigatie start. Gebruik dit voor het opwarmen van de pomp of het op druk brengen van het systeem.",zone_maximum_duration:"Harde bovengrens voor één enkele irrigatierun in seconden. Voorkomt ongecontroleerd water geven. Standaard: 3600 s (1 uur).",zone_linked_entity:"De HA-schakelaar- of klep-entiteit die de waterstroom voor deze zone regelt. Deze entiteit wordt ingeschakeld wanneer de irrigatie draait.",zone_flow_sensor:"Optionele sensor die het werkelijke waterdebiet meet. Alleen voor rapportage — heeft geen invloed op duurberekeningen.",general_autoupdatedelay:"Seconden om te wachten na het starten van HA voordat de eerste weergegevens worden opgehaald. Geeft andere integraties de kans om eerst te initialiseren.",general_sensor_debounce:"Minimale tussentijd in milliseconden tussen sensormetingen om ruis van snel veranderende sensoren weg te filteren.",general_calctime:"Tijdstip van de dag waarop de irrigatieduren opnieuw worden berekend uit de verzamelde weergegevens. Formaat: UU:MM (24-uurs).",general_cleardatatime:"Tijdstip van de dag waarop oude weergegevens worden gewist. Moet later worden ingesteld dan de berekeningstijd.",general_days_between:"Minimum aantal dagen tussen irrigatiebeurten voor dezelfde zone. Zet op 0 om uit te schakelen (irrigeren zodra er een tekort is).",general_autoupdateinterval:"Hoe vaak weergegevens worden verzameld. Kies een waarde die verse gegevens afweegt tegen API-limieten.",general_precipitation_threshold:"Irrigatie wordt overgeslagen als de voorspelde neerslag voor vandaag/morgen deze hoeveelheid overschrijdt.",general_temp_threshold:"Irrigatie wordt overgeslagen als de huidige temperatuur onder deze waarde ligt (bijv. om vorstschade te voorkomen).",general_wind_threshold:"Irrigatie wordt overgeslagen als de windsnelheid deze waarde overschrijdt (harde wind vermindert de efficiëntie en veroorzaakt drift)."},ki={title:"Configuratiewizard",open_button:"Configuratiewizard",close:"Sluiten",next:"Volgende",back:"Terug",finish:"Voltooien",skip_step:"Deze stap overslaan",step_indicator:"Stap {current} van {total}",setup_complete_banner:"Configuratie niet voltooid. Voer de wizard uit om te beginnen.",open_wizard:"Wizard openen",steps:{welcome:{title:"Welkom bij Smart Irrigation",intro:"Deze wizard leidt je door de vier stappen die nodig zijn om je eerste zone automatisch te laten irrigeren.",step1_label:"Weerdienst — waar de weergegevens vandaan komen",step2_label:"Berekeningsmodule — hoe de irrigatieduur wordt berekend",step3_label:"Sensorgroep — welke gegevensbronnen te gebruiken",step4_label:"Zone — je eerste irrigatiezone",tip:"Je kunt elke stap overslaan en deze later configureren via het tabblad Instellen."},weather:{title:"Weerdienst",description:"Kies hoe je weergegevens ophaalt. Open-Meteo is gratis en vereist geen API-sleutel — de eenvoudigste keuze voor de meeste gebruikers."},module:{title:"Berekeningsmodule",description:"Een module berekent hoe lang te irrigeren op basis van evapotranspiratie (ET). De PyETO-module (FAO-56-methode) wordt voor de meeste gebruikers aanbevolen.",pick_label:"Moduletype selecteren",no_modules:"Geen moduletypen beschikbaar."},mapping:{title:"Sensorgroep",description:"Een sensorgroep koppelt elke weervariabele aan een gegevensbron. Stel hieronder de belangrijkste variabelen in — afzonderlijke sensortoewijzingen kun je later verfijnen via het tabblad Instellen → Sensorgroepen.",name_label:"Naam van de sensorgroep",source_label:"Gegevensbron voor",use_weather_service:"Weerdienst",use_sensor:"Sensor",use_static:"Statische waarde",use_none:"Geen / niet gebruikt"},zone:{title:"Eerste zone",description:"Een zone is één irrigatiegebied (bijv. gazon, plantenbed). Stel de fysieke eigenschappen in zodat het systeem de juiste irrigatieduur kan berekenen.",name_label:"Zonenaam",size_label:"Oppervlak",throughput_label:"Sproeierdoorvoer",entity_label:"Gekoppelde schakelaar of klep",entity_placeholder:"bijv. switch.garden_valve",module_label:"Berekeningsmodule",mapping_label:"Sensorgroep"},done:{title:"Configuratie voltooid!",description:"Je eerste zone is klaar. Smart Irrigation berekent nu automatisch de irrigatieduren op basis van weergegevens.",next_steps:"Wat je hierna kunt doen:",tip1:"Ga naar Zones om de berekende duren en emmerwaarden te bekijken.",tip2:"Voeg meer zones toe via het tabblad Zones.",tip3:"Verfijn alle instellingen via het tabblad Instellen.",go_zones:"Naar Zones",go_setup:"Naar Instellen"}}},zi={common:di,defaults:ui,module:ci,calcmodules:pi,panels:hi,title:gi,coordinate_config:mi,days_between_irrigation:vi,irrigation_start_triggers:fi,weather_skip:_i,zone_sequencing:bi,weather_service_config:yi,field_help:wi,wizard:ki},Si=Object.freeze({__proto__:null,common:di,defaults:ui,module:ci,calcmodules:pi,panels:hi,title:gi,coordinate_config:mi,days_between_irrigation:vi,irrigation_start_triggers:fi,weather_skip:_i,zone_sequencing:bi,weather_service_config:yi,field_help:wi,wizard:ki,default:zi}),xi={actions:{delete:"Slett",edit:"Rediger",save:"Lagre",cancel:"Avbryt",confirm_delete:"Bekreft sletting",confirm_delete_zone:"Er du sikker på at du vil slette denne sonen?"},labels:{module:"Modul",no:"Nei",select:"Velg",yes:"Ja",enabled:"Aktivert",disabled:"Deaktivert",before:"før",after:"etter",settings:"Innstillinger",bulk_actions:"Masseoperasjoner"},attributes:{size:"størrelse",throughput:"kapasitet",state:"status",bucket:"beholder",last_updated:"sist oppdatert",last_calculated:"sist beregnet",number_of_data_points:"antall datapunkter"},loading:"Laster",saving:"Lagrer",units:{seconds:"sekunder"},"loading-messages":{configuration:"Laster konfigurasjon...",modules:"Laster moduler...",general:"Laster..."},"saving-messages":{adding:"Legger til...",saving:"Lagrer..."},errors:{load_failed:"Kunne ikke laste data",save_failed:"Kunne ikke lagre endringene",delete_failed:"Kunne ikke slette",action_failed:"Handlingen mislyktes"}},$i={"default-zone":"Standard sone","default-mapping":"Standard sensorguppe"},Ai={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Merk: Denne forklaringen bruker '.' som desimaltegn og viser avrundede verdier. Modulen returnerte evapotranspirasjonsunderskudd på","bucket-was":"Bucket var","new-bucket-values-is":"Ny bucket verdien er","old-bucket-variable":"gammel_bucket",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Siden bucket < 0, Vanning er nødvendig.","steps-taken-to-calculate-duration":"For å beregne nøyaktig varighet, ble følgende trinn utført","precipitation-rate-defined-as":"Nedbørshastigheten er definert som","duration-is-calculated-as":"Varigheten beregnes som",bucket:"bøtte","precipitation-rate-variable":"nedbørshastighet","multiplier-is-applied":"Nå blir multiplikatoren brukt. Multiplikatoren er","duration-after-multiplier-is":"derfor er varigheten","maximum-duration-is-applied":"Deretter blir den maksimale varigheten brukt. Den maksimale varigheten er","duration-after-maximum-duration-is":"derfor er varigheten","lead-time-is-applied":"Til slutt blir ledetiden brukt. Ledetiden er","duration-after-lead-time-is":"derfor er den endelige varigheten","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Siden bucket >= 0, Ingen vanning er nødvendig, og varigheten er satt til","maximum-bucket-is":"maksimum bucket stærrelse er","max-bucket-variable":"max_bucket",drainage:"drenering","drainage-rate":"dreneringsrate",hours:"timer","drainage-rate-is":"Dreneringshastigheten ved metning (beholder på maks) er","current-drainage-is":"Gjeldende drenering beregnet som","no-drainage":"Gjeldende drenering er 0 fordi"}}},Mi={pyeto:{description:"Beregn varigheten basert på FAO56-beregningen fra PyETO-biblioteket"},static:{description:"'Dummy'-modul med en statisk konfigurerbar endring (delta)"},passthrough:{description:"En 'Passthrough'-modul som returnerer verdien av en Evapotranspiration-sensor som delta"}},Ei={general:{cards:{"automatic-duration-calculation":{header:"Automatisk varighetsberegning",labels:{"auto-calc-enabled":"Beregn sonevarigheter automatisk","auto-calc-time":"Beregn ved","calc-time":"Beregn kl."},description:"Beregningen bruker værdataene som er samlet inn frem til da, og oppdaterer bøtten for hver automatiske sone. Deretter justeres varigheten basert på den nye bøtteverdien, og de innsamlede værdataene fjernes."},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Advarsel: Oppdateringstidspunkt for værdata på eller etter beregningstidspunktet"},header:"Automatisk oppdatering av værdata",labels:{"auto-update-enabled":"Oppdater værdata automatisk","auto-update-first-update":"(Første) Oppdatering kl","auto-update-interval":"Oppdater sensordata hvert","auto-update-schedule":"Oppdateringsplan","auto-update-time":"Oppdater kl.","auto-update-delay":"Oppdateringsforsinkelse"},options:{days:"dager",hours:"timer",minutes:"minutter"},description:"Samle inn og lagre værdata automatisk. Værdata kreves for å beregne sonebøtter og varigheter."},"automatic-clear":{header:"Automatisk rydding av værdata",description:"Fjern innsamlede værdata automatisk på et konfigurert tidspunkt. Bruk dette for å sikre at det ikke er igjen værdata fra tidligere dager. Ikke fjern værdataene før du beregner, og bruk bare dette alternativet hvis du forventer at den automatiske oppdateringen samler inn værdata etter at du har beregnet for dagen. Ideelt sett rydder du så sent på dagen som mulig.",labels:{"automatic-clear-enabled":"Tøm innsamlede værdata automatisk","automatic-clear-time":"Tøm værdata kl."}},continuousupdates:{header:"Kontinuerlige sensoroppdateringer (eksperimentell)",description:"Eksperimentell funksjon for mer granulære værdata.",labels:{continuousupdates:"Aktiver kontinuerlige oppdateringer",sensor_debounce:"Sensor-debounce","sensor-debounce":"Sensor-debouncetid (ms)"}}},description:"Denne siden gir globale innstillinger.",title:"Generelt"},help:{title:"Hjelp",cards:{"how-to-get-help":{title:"Hvordan få hjelp","first-read-the":"Først, les",wiki:"Dokumentasjon","if-you-still-need-help":"Hvis du fremdeles trenger hjelp, ta kontakt på","community-forum":"Fellesskapsforumet","or-open-a":"eller åpne en","github-issue":"Github-sak","english-only":"Kun på engelsk"}}},mappings:{cards:{"add-mapping":{actions:{add:"Legg til sensorguppe"},header:"Legg til sensorgupper"},mapping:{aggregates:{average:"Gjennomsnitt",first:"Første",last:"Siste",maximum:"Maksimum",median:"Median",minimum:"Minimum",sum:"Sum",riemannsum:"Riemann-sum",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"Du kan ikke slette denne sensorguppen fordi minst én sone bruker den.",invalid_source:"Ugyldig kilde",source_does_not_exist:"Kilden finnes ikke. Angi en gyldig kilde, for eksempel 'sensor.mysensor'."},items:{dewpoint:"Duggpunkt",evapotranspiration:"Evapotranspirasjon",humidity:"Luftfuktighet","maximum temperature":"Maksimumstemperatur","minimum temperature":"Minimumstemperatur",precipitation:"Total nedbør",pressure:"Trykk","solar radiation":"Solstråling",temperature:"Temperatur",windspeed:"Vindhastighet","current precipitation":"Nåværende nedbør"},"sensor-aggregate-of-sensor-values-to-calculate":"av sensordata for å beregne varighet","sensor-aggregate-use-the":"Bruk","sensor-entity":"Sensorenhet",static_value:"Verdi","input-units":"Inndata gir verdier i",source:"Kilde",sources:{none:"Ingen",weather_service:"Værtjeneste",sensor:"Sensor",static:"Statisk verdi"},pressure_types:{absolute:"absolutt",relative:"relativ"},"pressure-type":"Trykket er"}},description:"Legg til en eller flere sensorgupper som henter værdata fra Weather service, fra sensorer eller en kombinasjon av disse. Du kan tilordne hver sensorguppe til en eller flere soner",labels:{"mapping-name":"Navn"},no_items:"Det er ingen definerte sensorgupper ennå.",title:"Sensorgupper","weather-records":{title:"Værregistreringer",timestamp:"Tid",temperature:"Temp.",humidity:"Humidity",precipitation:"Nedbør","retrieval-time":"Hentet","no-data":"Ingen værdata tilgjengelig for denne sensorgruppen",dewpoint:"Dugg",wind:"Vind",pressure:"Trykk"}},modules:{cards:{"add-module":{actions:{add:"Legg til modul"},header:"Legg til modul"},module:{errors:{"cannot-delete-module-because-zones-use-it":"Du kan ikke slette denne modulen fordi minst én sone bruker den."},labels:{configuration:"Konfigurasjon",required:"indikerer et obligatorisk felt"},"translated-options":{DontEstimate:"Ikke beregn",EstimateFromSunHours:"Beregn fra soltimer",EstimateFromTemp:"Beregn fra temperatur",EstimateFromSunHoursAndTemperature:"Estimer fra gjennomsnittet av soltimer og temperatur"}}},description:"Legg til en eller flere moduler som beregner vanningsvarighet. Hver modul har sin egen konfigurasjon og kan brukes til å beregne varighet for en eller flere soner.",no_items:"Det er ingen definerte moduler ennå.",title:"Moduler"},zones:{actions:{add:"Legg til",calculate:"Beregn",information:"Informasjon",update:"Oppdater","reset-bucket":"Nullstill bøtte","view-weather-info":"Se værdata","view-weather-info-message":"Værdata tilgjengelig for","view-watering-calendar":"Vanningskalender",irrigate_all:"Kjør alle soner nå"},cards:{"add-zone":{actions:{add:"Legg til sone"},header:"Legg til sone"},"zone-actions":{actions:{"calculate-all":"Beregn alle soner","update-all":"Oppdater alle soner","reset-all-buckets":"Nullstill alle bøtter","clear-all-weatherdata":"Tøm alle værdata"},header:"Handlinger på alle soner"}},description:"Spesifiser en eller flere vanningssoner her. Vanningens varighet beregnes per sone, avhengig av størrelse, gjennomstrømning, tilstand, modul og sensorguppe.",labels:{bucket:"Bøtte",duration:"Varighet","lead-time":"Ledetid",mapping:"Sensorguppe","maximum-duration":"Maksimal varighet",multiplier:"Multiplikator",name:"Navn",size:"Størrelse",state:"Tilstand",states:{automatic:"Automatisk",disabled:"Deaktivert",manual:"Manuell"},throughput:"Gjennomstrømning","maximum-bucket":"Maksimal bøtte",last_calculated:"Sist beregnet","data-last-updated":"Data sist oppdatert","data-number-of-data-points":"Antall datapunkter",drainage_rate:"Dreneringsrate",linked_entity:"Tilknyttet bryter/ventil-enhet",linked_entity_placeholder:"f.eks. switch.hage_ventil",irrigate_now:"Vann nå",bucket_threshold:"Minimum underskudd for vanning",flow_sensor:"Strømningsmåler-sensor (valgfritt)",flow_sensor_placeholder:"f.eks. sensor.zone_flow_rate"},no_items:"Det er ingen definerte soner ennå.",title:"Soner",confirm_irrigate:{title:"Starte vanning?",body:"Dette åpner nå de tilkoblede ventilene og overstyrer alle hoppe-over-betingelser (regn, temperatur, minste antall dager mellom vanninger).",all_linked_zones:"Alle tilkoblede soner",toast_started:"Vanning startet",toast_failed:"Vanning mislyktes"}},title:"Smart vanning",schedules:{title:"Tidsplaner",description:"Opprett gjentakende tidsplaner for automatisk beregning, oppdatering eller vanning — uten automatiseringer.",add:"Legg til tidsplan",no_items:"Ingen tidsplaner konfigurert ennå. Klikk på 'Legg til tidsplan'.",zones_all:"Alle soner",zones_specific:"Spesifikke soner",hours:"timer",minutes:"min",types:{daily:"Daglig",weekly:"Ukentlig",monthly:"Månedlig",interval:"Hver N time",sunrise:"Soloppgang",sunset:"Solnedgang",solar_azimuth:"Solazimutt"},actions:{calculate:"Beregn (oppdater vanningsvarighet)",update:"Oppdater (samle inn værdata)",irrigate:"Vann (styr ventiler direkte)"},days:{monday:"Ma",tuesday:"Ti",wednesday:"On",thursday:"To",friday:"Fr",saturday:"Lø",sunday:"Sø"},fields:{name:"Navn",type:"Tidsplantype",enabled:"Aktivert",time:"Tid (HH:MM)",days_of_week:"Ukedager",day_of_month:"Dag i måneden",interval_hours:"Intervall",action:"Handling",zones:"Soner",start_date:"Startdato (valgfritt)",end_date:"Sluttdato (valgfritt)",offset_minutes:"Forskyvning fra soloppgang/-nedgang",account_for_duration:"Start tidlig slik at vanningen er ferdig til måltidspunktet",azimuth_angle:"Solazimutt-vinkel"},dialog:{add_title:"Legg til tidsplan",edit_title:"Rediger tidsplan"}},info:{title:"Info",description:"Vis informasjon om neste vanning og systemstatus.","configuration-not-available":"Konfigurasjon ikke tilgjengelig.",cards:{"zone-bucket-values":{title:"Sone-beholderverdier og varighet",labels:{bucket:"Beholder",duration:"Varighet"},"no-zones":"Ingen soner konfigurert"},"next-irrigation":{title:"Neste vanning",labels:{"next-start":"Neste start",duration:"Varighet",zones:"Soner"},"no-data":"Ingen data tilgjengelig"},"irrigation-reason":{title:"Årsak til vanning",labels:{reason:"Årsak",sunrise:"Soloppgang","total-duration":"Total varighet",explanation:"Forklaring"},"no-data":"Ingen data tilgjengelig"},irrigate_now:{title:"Vann nå",description:"Start vanning umiddelbart for alle soner med tilknyttet enhet. Hoppover-betingelser ignoreres.",button_all:"Start alle soner nå",no_linked_zones:"Ingen soner har en tilknyttet bryter/ventil-enhet med beregnet varighet."}}},setup:{title:"Oppsett"}},Ti={title:"Stedskoordinater",description:"Konfigurer stedskoordinater for innhenting av værdata. Du kan bruke manuelle koordinater som er forskjellige fra din Home Assistant plassering om nødvendig.",manual_enabled:"Bruk manuelle koordinater",use_ha_location:"Bruk Home Assistant plassering",latitude:"Breddegrad (desimalgrader)",longitude:"Lengdegrad (desimalgrader)",elevation:"Høyde (meter over havet)",current_ha_coords:"Gjeldende Home Assistant koordinater"},Di={title:"Dager mellom vanning",description:"Konfigurer minimumsantall dager mellom vanningshendelser.",label:"Minimum dager mellom vanning",help_text:"Sett til 0 for å deaktivere. Verdier fra 1-365 dager støttes."},ji="Smart Irrigation",Oi={title:"Utløsere for vanningsstart",description:"Konfigurer når vanningen skal starte basert på solhendelser. Du kan legge til flere utløsere for ulike tidsplaner. For soloppgangsutløsere vil et forskyvning på 0 automatisk bruke den totale varigheten av alle aktiverte soner.",add_trigger:"Legg til utløser",edit_trigger:"Rediger utløser",delete_trigger:"Slett utløser",trigger_types:{sunrise:"Soloppgang",sunset:"Solnedgang",solar_azimuth:"Solazimut"},fields:{name:{name:"Utløsernavn",description:"Et beskrivende navn for å identifisere denne utløseren"},type:{name:"Utløsertype",description:"Typen solhendelse å utløse på"},enabled:{name:"Aktivert",description:"Om denne utløseren er aktiv nå"},offset_minutes:{name:"Forskyvning (minutter)",description:"Minutter før (-) eller etter (+) solhendelsen. For soloppgangsutløsere, bruk 0 for automatisk timing basert på total sonevarighet."},azimuth_angle:{name:"Azimutvinkel (grader)",description:"Solazimutvinkel i grader der 0=Nord, 90=Øst, 180=Sør, 270=Vest"},account_for_duration:{name:"Ta hensyn til varighet",description:"Når aktivert starter vanningen tidlig nok til å bli ferdig til angitt tidspunkt. Når deaktivert starter vanningen nøyaktig på angitt tidspunkt."}},dialog:{add_title:"Legg til utløser for vanningsstart",edit_title:"Rediger utløser for vanningsstart",cancel:"Avbryt",save:"Lagre",delete:"Slett"},no_triggers:"Ingen utløsere for vanningsstart konfigurert. Systemet bruker standardatferden (soloppgang med total sonevarighet). Legg til utløsere for å tilpasse når vanningen starter.",offset_auto:"Automatisk (beregnet fra total sonevarighet)",confirm_delete:"Er du sikker på at du vil slette utløseren '{name}'?",validation:{name_required:"Utløsernavn er påkrevd",azimuth_invalid:"Azimutvinkelen må være et gyldig tall"},help:{sunrise_offset:"For soloppgangsutløsere: Bruk negative verdier for å starte før soloppgang, positive for å starte etter. Sett til 0 for automatisk å starte tidlig nok til å fullføre alle soner før soloppgang.",sunset_offset:"For solnedgangsutløsere: Bruk negative verdier for å starte før solnedgang, positive for å starte etter solnedgang.",azimuth_explanation:"Solazimut er kompassretningen til solen. 0°=Nord, 90°=Øst, 180°=Sør, 270°=Vest. Du kan angi en hvilken som helst vinkelverdi (f.eks. 450° = 90°, -30° = 330°). Bruk dette til å utløse vanning når solen når en bestemt posisjon.",multiple_triggers:"Du kan konfigurere flere utløsere. Hver aktiverte utløser planlegger vanningsstart uavhengig."}},Ci={title:"Hoppover-betingelser",description:"Hopp automatisk over vanning når forholdene er ugunstige. Nedbørs-, temperatur- og vindsjekker krever en værtjeneste.",threshold_label:"Nedbørsterskel",threshold_description:"Minimum mengde forventet nedbør (i mm) for i dag og morgen for å hoppe over vanning.",temp_section_title:"Hopp over ved lav temperatur",temp_threshold_label:"Hopp over hvis temperatur under",wind_section_title:"Hopp over ved sterk vind",wind_threshold_label:"Hopp over hvis vindhastighet over",rain_sensor_section_title:"Regnsensorbetingelse",rain_sensor_label:"Regnsensor-enhet (valgfritt)",rain_sensor_placeholder:"f.eks. binary_sensor.regn"},Pi={title:"Sonesekvens",description:"Når flere soner trenger vanning, velg om de kjører samtidig eller én etter én. I sekvensiell modus venter systemet til hver sone er ferdig før neste starter.",parallel:"Parallell (alle soner samtidig)",sequential:"Sekvensiell (én sone om gangen)",rotating:"Roterende (soner bytter på)",max_consecutive_duration_label:"Maks. sammenhengende kjøretid per sone",max_consecutive_duration_unit:"minutter",min_absorption_time_label:"Min. absorpsjonstid mellom økter",min_absorption_time_unit:"minutter (0 = deaktivert)"},Ni={title:"Værtjeneste",description:"Konfigurer hvilken værtjeneste som skal brukes for ET-beregninger og hopp over-betingelser.",enabled_label:"Aktiver værtjeneste",service_label:"Værtjeneste",api_key_label:"API-nøkkel",api_key_placeholder:"La stå tom for å beholde eksisterende nøkkel",api_key_configured:"API-nøkkel er konfigurert",api_key_not_configured:"Ingen API-nøkkel konfigurert",api_key_help:"En API-nøkkel fra den valgte værtjenesteleverandøren din. Open-Meteo krever ingen nøkkel. OpenWeatherMap og Pirate Weather tilbyr begge gratis nivåer.",no_api_key_needed:"Open-Meteo er en gratis tjeneste og krever ingen API-nøkkel.",save_button:"Lagre værinnstillinger",saved:"Værinnstillinger lagret",openmeteo:"Open-Meteo (gratis, ingen nøkkel nødvendig)",test_button:"Test tilkobling",test_button_testing:"Tester…",test_success:"✓ Tilkobling vellykket",test_error_invalid_auth:"✗ Ugyldig API-nøkkel — sjekk at den er riktig og aktiv",test_error_cannot_connect:"✗ Kan ikke koble til — sjekk internettforbindelsen din",test_error_no_service:"✗ Velg en værtjeneste først",test_error_unknown:"✗ Test mislyktes — ukjent feil",owm:"OpenWeatherMap",pw:"Pirate Weather"},Hi={zone_size:"Det totale vannede arealet for denne sonen. Brukes sammen med gjennomstrømningen for å beregne hvor mye vann som tilføres per kjøring.",zone_throughput:"Total vanngjennomstrømning for vanningssystemet ditt for denne sonen (liter/min i metrisk, gal/min i imperisk). Sjekk databladet for sprederne dine eller mål ved å ta tiden på hvor lang tid det tar å fylle en beholder med kjent volum.",zone_drainage_rate:"Hvor raskt overflødig vann dreneres fra jorden når bøtten er full. Typisk: plen 50 mm/t, sandjord 100+ mm/t, leire 10 mm/t.",zone_bucket:"Nåværende vannunderskudd (negativt) eller -overskudd (positivt) for denne sonen. Vanning utløses når bøtten faller under terskelen.",zone_maximum_bucket:"Maksimalt fuktoverskudd sonen kan holde på. Vann over dette nivået behandles som avrenning. Typisk verdi: 50 mm.",zone_bucket_threshold:"Vanning utløses når bøtten faller under denne verdien. Må være 0 eller negativ. 0 betyr å vanne så snart det er et underskudd.",zone_multiplier:"Skaleringsfaktor som brukes på den beregnede varigheten. Over 1,0 øker, under 1,0 reduserer. Nyttig for finjustering uten å endre fysiske målinger.",zone_lead_time:"Ekstra sekunder før vanningen starter. Bruk dette for oppvarming av pumpen eller trykksetting av systemet.",zone_maximum_duration:"Hard øvre grense for én enkelt vanningskjøring i sekunder. Hindrer ukontrollert vanning. Standard: 3600 s (1 time).",zone_linked_entity:"HA-bryter- eller ventilenheten som styrer vannstrømmen for denne sonen. Denne enheten slås på når vanningen kjører.",zone_flow_sensor:"Valgfri sensor som måler faktisk vannstrømningsrate. Brukes bare til rapportering — påvirker ikke varighetsberegninger.",general_autoupdatedelay:"Sekunder å vente etter at HA starter før første henting av værdata. Lar andre integrasjoner initialisere først.",general_sensor_debounce:"Minimum mellomrom i millisekunder mellom sensoravlesninger for å filtrere bort støy fra raskt skiftende sensorer.",general_calctime:"Tidspunkt på dagen da vanningsvarighetene beregnes på nytt fra innsamlede værdata. Format: TT:MM (24-timers).",general_cleardatatime:"Tidspunkt på dagen da gamle værdata slettes. Må settes senere enn beregningstidspunktet.",general_days_between:"Minimum antall dager mellom vanninger for samme sone. Sett til 0 for å deaktivere (vann så snart det er et underskudd).",general_autoupdateinterval:"Hvor ofte værdata samles inn. Velg en verdi som balanserer ferske data mot API-grenser.",general_precipitation_threshold:"Vanning hoppes over hvis varslet nedbør for i dag/i morgen overstiger denne mengden.",general_temp_threshold:"Vanning hoppes over hvis nåværende temperatur er under denne verdien (f.eks. for å forhindre frostskade).",general_wind_threshold:"Vanning hoppes over hvis vindhastigheten overstiger denne verdien (sterk vind reduserer effektiviteten og forårsaker avdrift)."},Ii={title:"Oppsettsveiviser",open_button:"Oppsettsveiviser",close:"Lukk",next:"Neste",back:"Tilbake",finish:"Fullfør",skip_step:"Hopp over dette trinnet",step_indicator:"Trinn {current} av {total}",setup_complete_banner:"Oppsett ikke fullført. Kjør veiviseren for å komme i gang.",open_wizard:"Åpne veiviser",steps:{welcome:{title:"Velkommen til Smart Irrigation",intro:"Denne veiviseren leder deg gjennom de fire trinnene som trengs for å få den første sonen din til å vanne automatisk.",step1_label:"Værtjeneste — hvor værdataene hentes fra",step2_label:"Beregningsmodul — hvordan vanningsvarigheten beregnes",step3_label:"Sensorgruppe — hvilke datakilder som skal brukes",step4_label:"Sone — din første vanningssone",tip:"Du kan hoppe over et hvilket som helst trinn og konfigurere det senere fra Oppsett-fanen."},weather:{title:"Værtjeneste",description:"Velg hvordan værdata hentes. Open-Meteo er gratis og krever ingen API-nøkkel — det enkleste valget for de fleste."},module:{title:"Beregningsmodul",description:"En modul beregner hvor lenge det skal vannes basert på evapotranspirasjon (ET). PyETO-modulen (FAO-56-metoden) anbefales for de fleste.",pick_label:"Velg modultype",no_modules:"Ingen modultyper tilgjengelig."},mapping:{title:"Sensorgruppe",description:"En sensorgruppe kobler hver værvariabel til en datakilde. Angi nøkkelvariablene nedenfor — du kan finjustere individuelle sensortilordninger senere fra Oppsett → Sensorgrupper-fanen.",name_label:"Navn på sensorgruppe",source_label:"Datakilde for",use_weather_service:"Værtjeneste",use_sensor:"Sensor",use_static:"Statisk verdi",use_none:"Ingen / ikke brukt"},zone:{title:"Første sone",description:"En sone er ett vanningsområde (f.eks. plen, bed). Angi de fysiske egenskapene slik at systemet kan beregne riktig vanningsvarighet.",name_label:"Sonenavn",size_label:"Areal",throughput_label:"Spredergjennomstrømning",entity_label:"Tilkoblet bryter eller ventil",entity_placeholder:"f.eks. switch.garden_valve",module_label:"Beregningsmodul",mapping_label:"Sensorgruppe"},done:{title:"Oppsett fullført!",description:"Den første sonen din er klar. Smart Irrigation vil nå beregne vanningsvarigheter automatisk basert på værdata.",next_steps:"Hva du kan gjøre videre:",tip1:"Gå til Soner for å se beregnede varigheter og bøtteverdier.",tip2:"Legg til flere soner fra Soner-fanen.",tip3:"Finjuster alle innstillinger fra Oppsett-fanen.",go_zones:"Gå til Soner",go_setup:"Gå til Oppsett"}}},Li={common:xi,defaults:$i,module:Ai,calcmodules:Mi,panels:Ei,coordinate_config:Ti,days_between_irrigation:Di,title:ji,irrigation_start_triggers:Oi,weather_skip:Ci,zone_sequencing:Pi,weather_service_config:Ni,field_help:Hi,wizard:Ii},Bi=Object.freeze({__proto__:null,common:xi,defaults:$i,module:Ai,calcmodules:Mi,panels:Ei,coordinate_config:Ti,days_between_irrigation:Di,title:ji,irrigation_start_triggers:Oi,weather_skip:Ci,zone_sequencing:Pi,weather_service_config:Ni,field_help:Hi,wizard:Ii,default:Li}),Ui={actions:{delete:"Zmazať",edit:"Upraviť",save:"Uložiť",cancel:"Zrušiť",confirm_delete:"Potvrdiť odstránenie",confirm_delete_zone:"Naozaj chceš odstrániť túto zónu?"},labels:{module:"Modul",no:"Nie",select:"Zvoliť",yes:"Áno",enabled:"Povolené",disabled:"Zakázané",before:"pred",after:"po",settings:"Nastavenia",bulk_actions:"Hromadné akcie"},attributes:{size:"veľkosť",throughput:"priepustnosť",state:"stav",bucket:"zásobník",last_updated:"posledná aktualizácia",last_calculated:"posledný výpočet",number_of_data_points:"počet dátových bodov"},loading:"Načítanie",saving:"Ukladanie",units:{seconds:"sekúnd"},"loading-messages":{configuration:"Načítanie konfigurácie...",modules:"Načítanie modulov...",general:"Načítanie..."},"saving-messages":{adding:"Pridávanie...",saving:"Ukladanie..."},errors:{load_failed:"Údaje sa nepodarilo načítať",save_failed:"Zmeny sa nepodarilo uložiť",delete_failed:"Nepodarilo sa odstrániť",action_failed:"Akcia zlyhala"}},Ri={"default-zone":"Predvolená zóna","default-mapping":"Predvolená skupina snímačov"},Wi={calculation:{explanation:{"module-returned-evapotranspiration-deficiency":"Poznámka: toto vysvetlenie používa '.' ako oddeľovač desatinných miest zobrazuje zaokrúhlené a metrické hodnoty. Modul vrátil nedostatok evapotranspirácie","bucket-was":"Vedro bolo","new-bucket-values-is":"Hodnota nového vedra je","old-bucket-variable":"staré_vedro",delta:"delta","bucket-less-than-zero-irrigation-necessary":"Keďže vedro < 0, je potrebné zavlažovanie","steps-taken-to-calculate-duration":"Na výpočet presného trvania sa vykonali nasledujúce kroky","precipitation-rate-defined-as":"Miera zrážok je definovaná ako","duration-is-calculated-as":"Trvanie sa vypočíta ako",bucket:"vedro","precipitation-rate-variable":"úhrn zrážok","multiplier-is-applied":"Teraz sa použije multiplikátor. Násobiteľ je","duration-after-multiplier-is":"teda trvanie je","maximum-duration-is-applied":"Potom sa použije maximálne trvanie. Maximálne trvanie je","duration-after-maximum-duration-is":"teda trvanie je","lead-time-is-applied":"Nakoniec sa použije dodacia lehota. Dodacia lehota je","duration-after-lead-time-is":"teda konečné trvanie je","bucket-larger-than-or-equal-to-zero-no-irrigation-necessary":"Keďže vedro >= 0, nie je potrebné žiadne zavlažovanie a trvanie je nastavené na","maximum-bucket-is":"maximálna veľkosť vedra je","max-bucket-variable":"max_bucket",drainage:"odvodnenie","drainage-rate":"miera odvodnenia",hours:"hodiny","drainage-rate-is":"Rýchlosť odtoku pri nasýtení (zásobník na maxime) je","current-drainage-is":"Aktuálna drenáž vypočítaná ako","no-drainage":"Aktuálna drenáž je 0, pretože"}}},Fi={pyeto:{description:"Vypočítajte trvanie na základe výpočtu FAO56 z knižnice PyETO"},static:{description:"'Atrapa' modul so statickou konfigurovateľnou deltou"},passthrough:{description:"Priechodný modul, ktorý vracia hodnotu evapotranspiračného senzora ako delta"}},qi={general:{cards:{"automatic-duration-calculation":{header:"Automatický výpočet trvania",description:"Výpočet berie zhromaždené údaje o počasí až do tohto bodu a aktualizuje vedro pre každú automatickú zónu. Potom sa trvanie upraví na základe novej hodnoty segmentu a zhromaždené údaje o počasí sa odstránia.",labels:{"auto-calc-enabled":"Automaticky vypočítajte trvanie zón","auto-calc-time":"Vypočítajte pri","calc-time":"Vypočítať o"}},"automatic-update":{errors:{"warning-update-time-on-or-after-calc-time":"Upozornenie: Čas aktualizácie údajov o počasí v čase výpočtu alebo po ňom"},header:"Automatická aktualizácia poveternostných údajov",description:"Automaticky zbierajte a ukladajte údaje o počasí. Údaje o počasí sú potrebné na výpočet segmentov zón a trvania.",labels:{"auto-update-enabled":"Automaticky aktualizovať údaje o počasí","auto-update-delay":"Oneskorenie aktualizácie","auto-update-interval":"Aktualizujte údaje snímača každý","auto-update-schedule":"Plán aktualizácie","auto-update-time":"Aktualizovať o"},options:{days:"dni",hours:"hodiny",minutes:"minúty"}},"automatic-clear":{header:"Automatické orezávanie údajov o počasí",description:"Automaticky odstráňte zhromaždené údaje o počasí v nakonfigurovanom čase. Použite to, aby ste sa uistili, že nezostali žiadne údaje o počasí z predchádzajúcich dní. Neodstraňujte údaje o počasí pred výpočtom a túto možnosť použite iba vtedy, ak očakávate, že automatická aktualizácia bude zhromažďovať údaje o počasí až po výpočte na daný deň. V ideálnom prípade chcete prerezávať tak neskoro, ako je to možné.",labels:{"automatic-clear-enabled":"Automaticky vymazať zhromaždené údaje o počasí","automatic-clear-time":"Vymazať údaje o počasí o"}},continuousupdates:{header:"Priebežné aktualizácie senzorov (experimentálne)",description:"Experimentálna funkcia pre podrobnejšie meteorologické dáta.",labels:{continuousupdates:"Povoliť priebežné aktualizácie",sensor_debounce:"Debounce senzora","sensor-debounce":"Čas odrazu senzora (ms)"}}},description:"Táto stránka poskytuje globálne nastavenia.",title:"Všeobecné"},help:{title:"Pomoc",cards:{"how-to-get-help":{title:"Ako získať pomoc","first-read-the":"Najprv si prečítajte",wiki:"Dokumentácia","if-you-still-need-help":"Ak stále potrebujete pomoc, obráťte sa na","community-forum":"komunitné fórum","or-open-a":"alebo otvorte a","github-issue":"Problém Github","english-only":"len anglicky"}}},mappings:{cards:{"add-mapping":{actions:{add:"Pridať skupinu snímačov"},header:"Pridajte skupiny senzorov"},mapping:{aggregates:{average:"Priemer",first:"Prvý",last:"Posledný",maximum:"Maximum",median:"Medián",minimum:"Minimum",sum:"Súčet",riemannsum:"Riemannova suma",delta:"Delta"},errors:{"cannot-delete-mapping-because-zones-use-it":"Túto skupinu senzorov nemôžete vymazať, pretože ju používa aspoň jedna zóna.",invalid_source:"Neplatný zdroj",source_does_not_exist:"Zdroj neexistuje. Zadaj platný zdroj, napríklad 'sensor.mysensor'."},items:{dewpoint:"Rosný bod",evapotranspiration:"Evapotranspirácia",humidity:"Vlhkosť","maximum temperature":"Maximálna teplota","minimum temperature":"Minimálna teplota",precipitation:"Úhrn zrážok",pressure:"Tlak","solar radiation":"Slnečné žiarenie",temperature:"Teplota",windspeed:"Rýchlosť vetra","current precipitation":"Aktuálne zrážky"},pressure_types:{absolute:"absolútne",relative:"relatítne"},"pressure-type":"Tlak je","sensor-aggregate-of-sensor-values-to-calculate":"hodnôt snímača na výpočet trvania","sensor-aggregate-use-the":"Použiť","sensor-entity":"Entita snímača",static_value:"Hodnota","input-units":"Vstup poskytuje hodnoty v",source:"Zdroj",sources:{none:"Nie je",weather_service:"Poveternostná služba",sensor:"Snímač",static:"Statická hodnota"}}},description:"Pridajte jednu alebo viac skupín senzorov, ktoré získavajú údaje o počasí z Weather service, zo senzorov alebo ich kombinácie. Každú skupinu senzorov môžete namapovať na jednu alebo viac zón",labels:{"mapping-name":"Názov"},no_items:"Zatiaľ nie je definovaná žiadna skupina senzorov.",title:"Skupiny senzorov","weather-records":{title:"Záznamy o počasí",timestamp:"Čas",temperature:"Tepl.",humidity:"Humidity",precipitation:"Zrážky","retrieval-time":"Získané","no-data":"Pre túto skupinu senzorov nie sú dostupné žiadne poveternostné údaje",dewpoint:"Rosa",wind:"Vietor",pressure:"Tlak"}},modules:{cards:{"add-module":{actions:{add:"Pridať modul"},header:"Pridať modul"},module:{errors:{"cannot-delete-module-because-zones-use-it":"Tento modul nemôžete vymazať, pretože ho používa aspoň jedna zóna."},labels:{configuration:"Konfigurácia",required:"označuje povinné pole"},"translated-options":{DontEstimate:"Bez odhadu",EstimateFromSunHours:"Odhad zo slnečných hodín",EstimateFromTemp:"Odhad z teploty",EstimateFromSunHoursAndTemperature:"Odhad z priemeru hodín slnečného svitu a teploty"}}},description:"Pridajte jeden alebo viac modulov, ktoré vypočítavajú trvanie zavlažovania. Každý modul sa dodáva s vlastnou konfiguráciou a možno ho použiť na výpočet trvania pre jednu alebo viac zón.",no_items:"Zatiaľ nie sú definované žiadne moduly.",title:"Moduly"},zones:{actions:{add:"Pridať",calculate:"Vypočítať",information:"Informácia",update:"Aktualizovať","reset-bucket":"Resetovať vedro","view-weather-info":"Zobraziť počasie","view-weather-info-message":"Poveternostné údaje dostupné pre","view-watering-calendar":"Kalendár zavlažovania",irrigate_all:"Spustiť všetky zóny teraz"},cards:{"add-zone":{actions:{add:"Pridať zónu"},header:"Pridať zónu"},"zone-actions":{actions:{"calculate-all":"Vypočítajte všetky zóny","update-all":"Aktualizujte všetky zóny","reset-all-buckets":"Obnovte všetky vedrá","clear-all-weatherdata":"Vymazať všetky údaje o počasí"},header:"Akcie vo všetkých zónach"}},description:"Tu špecifikujte jednu alebo viac zavlažovacích zón. Trvanie zavlažovania sa vypočíta pre zónu v závislosti od veľkosti, výkonu, stavu, modulu a skupiny senzorov.",labels:{bucket:"Vedro",duration:"Trvanie","lead-time":"Dodacia lehota",mapping:"Skupina senzorov","maximum-duration":"Maximálne trvanie",multiplier:"Násobiteľ",name:"Názov",size:"Veľkosť",state:"Stav",states:{automatic:"Automatický",disabled:"Zakázaný",manual:"Manuány"},throughput:"Priepustnosť","maximum-bucket":"Maximálne vedro",last_calculated:"Naposledy vypočítané","data-last-updated":"Údaje boli naposledy aktualizované","data-number-of-data-points":"Počet údajových bodov",drainage_rate:"Miera odvodnenia",linked_entity:"Prepojená entita prepínača/ventilu",linked_entity_placeholder:"napr. switch.zahradny_ventil",irrigate_now:"Zavlažiť teraz",bucket_threshold:"Minimálny deficit pre závlahu",flow_sensor:"Senzor prietokomera (voliteľné)",flow_sensor_placeholder:"napr. sensor.zone_flow_rate"},no_items:"Zatiaľ nie sú definované žiadne zóny.",title:"Zóny",confirm_irrigate:{title:"Spustiť zavlažovanie?",body:"Týmto sa teraz otvoria prepojené ventily a obídu sa všetky podmienky preskočenia (dážď, teplota, minimálny počet dní medzi zavlažovaniami).",all_linked_zones:"Všetky prepojené zóny",toast_started:"Zavlažovanie spustené",toast_failed:"Zavlažovanie zlyhalo"}},schedules:{title:"Plány",description:"Vytvorte opakujúce sa plány pre automatický výpočet, aktualizáciu alebo závlahu — bez automatizácií.",add:"Pridať plán",no_items:"Zatiaľ nie sú nakonfigurované žiadne plány. Kliknite na 'Pridať plán'.",zones_all:"Všetky zóny",zones_specific:"Konkrétne zóny",hours:"hodín",minutes:"min",types:{daily:"Denne",weekly:"Týždenne",monthly:"Mesačne",interval:"Každých N hodín",sunrise:"Východ slnka",sunset:"Západ slnka",solar_azimuth:"Slnečný azimut"},actions:{calculate:"Vypočítať (aktualizovať dobu závlahy)",update:"Aktualizovať (zbierať meteorologické dáta)",irrigate:"Zavlažiť (priamo ovládať ventily)"},days:{monday:"Po",tuesday:"Ut",wednesday:"St",thursday:"Št",friday:"Pi",saturday:"So",sunday:"Ne"},fields:{name:"Názov",type:"Typ plánu",enabled:"Povolené",time:"Čas (HH:MM)",days_of_week:"Dni v týždni",day_of_month:"Deň v mesiaci",interval_hours:"Interval",action:"Akcia",zones:"Zóny",start_date:"Dátum začiatku (voliteľné)",end_date:"Dátum konca (voliteľné)",offset_minutes:"Posun od východu/západu slnka",account_for_duration:"Spustiť skoro, aby závlaha skončila v cieľovom čase",azimuth_angle:"Uhol slnečného azimutu"},dialog:{add_title:"Pridať plán",edit_title:"Upraviť plán"}},info:{title:"Info",description:"Zobraziť informácie o ďalšej závlahe a stave systému.","configuration-not-available":"Konfigurácia nie je k dispozícii.",cards:{"zone-bucket-values":{title:"Hodnoty zásobníka zóny a trvanie",labels:{bucket:"Zásobník",duration:"Trvanie"},"no-zones":"Žiadne zóny nie sú nakonfigurované"},"next-irrigation":{title:"Ďalšia závlaha",labels:{"next-start":"Ďalší štart",duration:"Trvanie",zones:"Zóny"},"no-data":"Žiadne dáta k dispozícii"},"irrigation-reason":{title:"Dôvod závlahy",labels:{reason:"Dôvod",sunrise:"Východ slnka","total-duration":"Celková doba",explanation:"Vysvetlenie"},"no-data":"Žiadne dáta k dispozícii"},irrigate_now:{title:"Zavlažiť teraz",description:"Okamžite spustiť závlahu pre všetky zóny s prepojenou entitou. Podmienky preskočenia sú ignorované.",button_all:"Spustiť všetky zóny teraz",no_linked_zones:"Žiadna zóna nemá prepojenú entitu prepínača/ventilu s vypočítanou dobou."}}},setup:{title:"Nastavenie"}},Vi="Inteligentné zavlažovanie",Zi={title:"Súradnice Polohy",description:"Nakonfigurujte súradnice polohy pre získavanie meteorologických údajov. Môžete použiť manuálne súradnice odlišné od vašej polohy Home Assistant ak je to potrebné.",manual_enabled:"Použiť manuálne súradnice",use_ha_location:"Použiť polohu Home Assistant",latitude:"Zemepisná šírka (desatinné stupne)",longitude:"Zemepisná dĺžka (desatinné stupne)",elevation:"Nadmorská výška (metre nad morom)",current_ha_coords:"Aktuálne súradnice Home Assistant"},Yi={title:"Dni medzi závlahami",description:"Nakonfigurujte minimálny počet dní medzi záhradnými udalosťami.",label:"Minimálne dni medzi závlahami",help_text:"Nastavte na 0 pre deaktiváciu. Podporované sú hodnoty 1-365 dní."},Gi={title:"Spúšťače spustenia zavlažovania",description:"Nakonfiguruj, kedy sa má spustiť zavlažovanie na základe slnečných udalostí. Môžeš pridať viacero spúšťačov pre rôzne harmonogramy. Pri spúšťačoch východu slnka sa pri posune 0 automaticky použije celkové trvanie všetkých povolených zón.",add_trigger:"Pridať spúšťač",edit_trigger:"Upraviť spúšťač",delete_trigger:"Odstrániť spúšťač",trigger_types:{sunrise:"Východ slnka",sunset:"Západ slnka",solar_azimuth:"Slnečný azimut"},fields:{name:{name:"Názov spúšťača",description:"Popisný názov na identifikáciu tohto spúšťača"},type:{name:"Typ spúšťača",description:"Typ slnečnej udalosti, na ktorú sa má spustiť"},enabled:{name:"Povolené",description:"Či je tento spúšťač momentálne aktívny"},offset_minutes:{name:"Posun (minúty)",description:"Minúty pred (-) alebo po (+) slnečnej udalosti. Pri spúšťačoch východu slnka použi 0 pre automatické načasovanie na základe celkového trvania zón."},azimuth_angle:{name:"Uhol azimutu (stupne)",description:"Uhol slnečného azimutu v stupňoch, kde 0=sever, 90=východ, 180=juh, 270=západ"},account_for_duration:{name:"Zohľadniť trvanie",description:"Ak je povolené, zavlažovanie sa spustí dostatočne skoro, aby skončilo v zadanom čase. Ak je zakázané, zavlažovanie sa spustí presne v zadanom čase."}},dialog:{add_title:"Pridať spúšťač spustenia zavlažovania",edit_title:"Upraviť spúšťač spustenia zavlažovania",cancel:"Zrušiť",save:"Uložiť",delete:"Odstrániť"},no_triggers:"Nie sú nakonfigurované žiadne spúšťače spustenia zavlažovania. Systém použije predvolené správanie (východ slnka s celkovým trvaním zón). Pridaj spúšťače na prispôsobenie spustenia zavlažovania.",offset_auto:"Automaticky (vypočítané z celkového trvania zón)",confirm_delete:"Naozaj chceš odstrániť spúšťač '{name}'?",validation:{name_required:"Názov spúšťača je povinný",azimuth_invalid:"Uhol azimutu musí byť platné číslo"},help:{sunrise_offset:"Pri spúšťačoch východu slnka: použi záporné hodnoty na spustenie pred východom slnka, kladné na spustenie po ňom. Nastav na 0 na automatické spustenie dostatočne skoro, aby sa všetky zóny dokončili pred východom slnka.",sunset_offset:"Pri spúšťačoch západu slnka: použi záporné hodnoty na spustenie pred západom slnka, kladné na spustenie po západe slnka.",azimuth_explanation:"Slnečný azimut je kompasový smer slnka. 0°=sever, 90°=východ, 180°=juh, 270°=západ. Môžeš zadať ľubovoľnú hodnotu uhla (napr. 450° = 90°, -30° = 330°). Použi to na spustenie zavlažovania, keď slnko dosiahne konkrétnu polohu.",multiple_triggers:"Môžeš nakonfigurovať viacero spúšťačov. Každý povolený spúšťač naplánuje spustenie zavlažovania nezávisle."}},Ki={title:"Podmienky preskočenia",description:"Automaticky preskočiť závlahu pri nepriaznivých podmienkach. Kontroly zrážok, teploty a vetra vyžadujú počasiovú službu.",threshold_label:"Prah zrážok",threshold_description:"Minimálne množstvo predpokladaných zrážok (v mm) pre dnešok a zajtrajšok na preskočenie závlahy.",temp_section_title:"Preskočiť pri nízkej teplote",temp_threshold_label:"Preskočiť ak teplota pod",wind_section_title:"Preskočiť pri silnom vetre",wind_threshold_label:"Preskočiť ak rýchlosť vetra nad",rain_sensor_section_title:"Podmienka dažďového senzora",rain_sensor_label:"Entita dažďového senzora (voliteľné)",rain_sensor_placeholder:"napr. binary_sensor.dazd"},Xi={title:"Poradie zón",description:"Keď viacero zón potrebuje závlahu, vyberte, či prebiehajú súčasne alebo jedna po druhej. V sekvenčnom režime systém čaká, kým každá zóna skončí, pred spustením ďalšej.",parallel:"Paralelne (všetky zóny súčasne)",sequential:"Sekvenčne (jedna zóna naraz)",rotating:"Rotujúce (zóny sa striedajú)",max_consecutive_duration_label:"Max. súvislý čas behu na zónu",max_consecutive_duration_unit:"minúty",min_absorption_time_label:"Min. čas vsiaknutia medzi cyklami",min_absorption_time_unit:"minúty (0 = vypnuté)"},Ji={title:"Poveternostná služba",description:"Nakonfiguruj, ktorá poveternostná služba sa použije na výpočty ET a podmienky preskočenia.",enabled_label:"Povoliť poveternostnú službu",service_label:"Poveternostná služba",api_key_label:"API kľúč",api_key_placeholder:"Nechaj prázdne na zachovanie existujúceho kľúča",api_key_configured:"API kľúč je nakonfigurovaný",api_key_not_configured:"Nie je nakonfigurovaný žiadny API kľúč",api_key_help:"API kľúč od tebou zvoleného poskytovateľa poveternostnej služby. Open-Meteo nevyžaduje kľúč. OpenWeatherMap aj Pirate Weather ponúkajú bezplatné úrovne.",no_api_key_needed:"Open-Meteo je bezplatná služba a nevyžaduje API kľúč.",save_button:"Uložiť nastavenia počasia",saved:"Nastavenia počasia uložené",openmeteo:"Open-Meteo (zdarma, bez kľúča)",test_button:"Otestovať pripojenie",test_button_testing:"Testuje sa…",test_success:"✓ Pripojenie úspešné",test_error_invalid_auth:"✗ Neplatný API kľúč — skontroluj, či je správny a aktívny",test_error_cannot_connect:"✗ Nedá sa pripojiť — skontroluj svoje internetové pripojenie",test_error_no_service:"✗ Najprv vyber poveternostnú službu",test_error_unknown:"✗ Test zlyhal — neznáma chyba",owm:"OpenWeatherMap",pw:"Pirate Weather"},Qi={zone_size:"Celková zavlažovaná plocha tejto zóny. Používa sa spolu s prietokom na výpočet množstva vody aplikovaného počas jedného cyklu.",zone_throughput:"Celkový prietok vody tvojho zavlažovacieho systému pre túto zónu (litre/min v metrickej sústave, gal/min v imperiálnej). Skontroluj technický list svojich postrekovačov alebo zmeraj, ako dlho trvá naplnenie nádoby známeho objemu.",zone_drainage_rate:"Ako rýchlo prebytočná voda odteká z pôdy, keď je vedro plné. Typicky: trávnik 50 mm/h, piesočnatá pôda 100+ mm/h, íl 10 mm/h.",zone_bucket:"Aktuálny deficit (záporný) alebo prebytok (kladný) vody pre túto zónu. Zavlažovanie sa spustí, keď vedro klesne pod prahovú hodnotu.",zone_maximum_bucket:"Maximálny prebytok vlhkosti, ktorý zóna dokáže zadržať. Voda nad touto úrovňou sa považuje za odtok. Typická hodnota: 50 mm.",zone_bucket_threshold:"Zavlažovanie sa spustí, keď vedro klesne pod túto hodnotu. Musí byť 0 alebo záporná. 0 znamená zavlažovať vždy, keď je deficit.",zone_multiplier:"Mierka aplikovaná na vypočítané trvanie. Nad 1,0 zvyšuje, pod 1,0 znižuje. Užitočné na jemné doladenie bez zmeny fyzických meraní.",zone_lead_time:"Sekundy navyše pred spustením zavlažovania. Použi to na zahriatie čerpadla alebo natlakovanie systému.",zone_maximum_duration:"Pevný horný limit pre jeden zavlažovací cyklus v sekundách. Zabraňuje nekontrolovanému zavlažovaniu. Predvolené: 3600 s (1 hodina).",zone_linked_entity:"Entita prepínača alebo ventilu v HA, ktorá riadi prietok vody pre túto zónu. Táto entita sa zapne, keď beží zavlažovanie.",zone_flow_sensor:"Voliteľný senzor merajúci skutočný prietok vody. Používa sa len na vykazovanie — neovplyvňuje výpočet trvania.",general_autoupdatedelay:"Sekundy čakania po spustení HA pred prvým získaním poveternostných údajov. Umožňuje ostatným integráciám sa najprv inicializovať.",general_sensor_debounce:"Minimálny odstup v milisekundách medzi načítaniami senzora na odfiltrovanie šumu z rýchlo sa meniacich senzorov.",general_calctime:"Čas dňa, kedy sa trvania zavlažovania prepočítajú zo získaných poveternostných údajov. Formát: HH:MM (24-hodinový).",general_cleardatatime:"Čas dňa, kedy sa odstránia staré poveternostné údaje. Musí byť nastavený neskôr ako čas výpočtu.",general_days_between:"Minimálny počet dní medzi zavlažovaniami tej istej zóny. Nastav na 0 na vypnutie (zavlažovať vždy, keď je deficit).",general_autoupdateinterval:"Ako často sa získavajú poveternostné údaje. Zvoľ hodnotu, ktorá vyvažuje čerstvé údaje a limity API.",general_precipitation_threshold:"Zavlažovanie sa preskočí, ak predpovedané zrážky na dnes/zajtra prekročia toto množstvo.",general_temp_threshold:"Zavlažovanie sa preskočí, ak je aktuálna teplota pod touto hodnotou (napr. na zabránenie poškodeniu mrazom).",general_wind_threshold:"Zavlažovanie sa preskočí, ak rýchlosť vetra prekročí túto hodnotu (silný vietor znižuje účinnosť a spôsobuje úlet)."},en={title:"Sprievodca nastavením",open_button:"Sprievodca nastavením",close:"Zavrieť",next:"Ďalej",back:"Späť",finish:"Dokončiť",skip_step:"Preskočiť tento krok",step_indicator:"Krok {current} z {total}",setup_complete_banner:"Nastavenie nie je dokončené. Spusti sprievodcu a začni.",open_wizard:"Otvoriť sprievodcu",steps:{welcome:{title:"Vitaj v Smart Irrigation",intro:"Tento sprievodca ťa prevedie štyrmi krokmi potrebnými na to, aby tvoja prvá zóna automaticky zavlažovala.",step1_label:"Poveternostná služba — odkiaľ získať poveternostné údaje",step2_label:"Výpočtový modul — ako sa počíta trvanie zavlažovania",step3_label:"Skupina senzorov — ktoré zdroje údajov použiť",step4_label:"Zóna — tvoja prvá zavlažovacia zóna",tip:"Ktorýkoľvek krok môžeš preskočiť a nakonfigurovať ho neskôr na karte Nastavenie."},weather:{title:"Poveternostná služba",description:"Vyber, ako sa získavajú poveternostné údaje. Open-Meteo je zadarmo a nevyžaduje API kľúč — pre väčšinu používateľov najjednoduchšia voľba."},module:{title:"Výpočtový modul",description:"Modul vypočíta, ako dlho zavlažovať, na základe evapotranspirácie (ET). Modul PyETO (metóda FAO-56) sa odporúča pre väčšinu používateľov.",pick_label:"Vyber typ modulu",no_modules:"Nie sú dostupné žiadne typy modulov."},mapping:{title:"Skupina senzorov",description:"Skupina senzorov prepája každú poveternostnú premennú s dátovým zdrojom. Nastav kľúčové premenné nižšie — jednotlivé priradenia senzorov môžeš spresniť neskôr na karte Nastavenie → Skupiny senzorov.",name_label:"Názov skupiny senzorov",source_label:"Zdroj údajov pre",use_weather_service:"Poveternostná služba",use_sensor:"Senzor",use_static:"Statická hodnota",use_none:"Žiadny / nepoužité"},zone:{title:"Prvá zóna",description:"Zóna je jedna zavlažovaná plocha (napr. trávnik, záhon). Nastav fyzické vlastnosti, aby systém mohol vypočítať správne trvanie zavlažovania.",name_label:"Názov zóny",size_label:"Plocha",throughput_label:"Prietok postrekovača",entity_label:"Prepojený prepínač alebo ventil",entity_placeholder:"napr. switch.garden_valve",module_label:"Výpočtový modul",mapping_label:"Skupina senzorov"},done:{title:"Nastavenie dokončené!",description:"Tvoja prvá zóna je pripravená. Smart Irrigation teraz bude automaticky počítať trvania zavlažovania na základe poveternostných údajov.",next_steps:"Čo môžeš urobiť ďalej:",tip1:"Prejdi na Zóny a zobraz vypočítané trvania a hodnoty vedra.",tip2:"Pridaj ďalšie zóny na karte Zóny.",tip3:"Doladi všetky nastavenia na karte Nastavenie.",go_zones:"Prejsť na Zóny",go_setup:"Prejsť na Nastavenie"}}},tn={common:Ui,defaults:Ri,module:Wi,calcmodules:Fi,panels:qi,title:Vi,coordinate_config:Zi,days_between_irrigation:Yi,irrigation_start_triggers:Gi,weather_skip:Ki,zone_sequencing:Xi,weather_service_config:Ji,field_help:Qi,wizard:en},an=Object.freeze({__proto__:null,common:Ui,defaults:Ri,module:Wi,calcmodules:Fi,panels:qi,title:Vi,coordinate_config:Zi,days_between_irrigation:Yi,irrigation_start_triggers:Gi,weather_skip:Ki,zone_sequencing:Xi,weather_service_config:Ji,field_help:Qi,wizard:en,default:tn});function nn(e,t){var a=t&&t.cache?t.cache:gn,i=t&&t.serializer?t.serializer:dn;return(t&&t.strategy?t.strategy:ln)(e,{cache:a,serializer:i});}function sn(e,t,a,i){var n,s=null==(n=i)||"number"==typeof n||"boolean"==typeof n?i:a(i),r=t.get(s);return void 0===r&&(r=e.call(this,i),t.set(s,r)),r;}function rn(e,t,a){var i=Array.prototype.slice.call(arguments,3),n=a(i),s=t.get(n);return void 0===s&&(s=e.apply(this,i),t.set(n,s)),s;}function on(e,t,a,i,n){return a.bind(t,e,i,n);}function ln(e,t){return on(e,this,1===e.length?sn:rn,t.cache.create(),t.serializer);}var dn=function(){return JSON.stringify(arguments);};function un(){this.cache=Object.create(null);}un.prototype.get=function(e){return this.cache[e];},un.prototype.set=function(e,t){this.cache[e]=t;};var cn,pn,hn,gn={create:function(){return new un();}},mn={variadic:function(e,t){return on(e,this,rn,t.cache.create(),t.serializer);},monadic:function(e,t){return on(e,this,sn,t.cache.create(),t.serializer);}};function vn(e){return e.type===pn.literal;}function fn(e){return e.type===pn.argument;}function _n(e){return e.type===pn.number;}function bn(e){return e.type===pn.date;}function yn(e){return e.type===pn.time;}function wn(e){return e.type===pn.select;}function kn(e){return e.type===pn.plural;}function zn(e){return e.type===pn.pound;}function Sn(e){return e.type===pn.tag;}function xn(e){return!(!e||"object"!=typeof e||e.type!==hn.number);}function $n(e){return!(!e||"object"!=typeof e||e.type!==hn.dateTime);}!function(e){e[e.EXPECT_ARGUMENT_CLOSING_BRACE=1]="EXPECT_ARGUMENT_CLOSING_BRACE",e[e.EMPTY_ARGUMENT=2]="EMPTY_ARGUMENT",e[e.MALFORMED_ARGUMENT=3]="MALFORMED_ARGUMENT",e[e.EXPECT_ARGUMENT_TYPE=4]="EXPECT_ARGUMENT_TYPE",e[e.INVALID_ARGUMENT_TYPE=5]="INVALID_ARGUMENT_TYPE",e[e.EXPECT_ARGUMENT_STYLE=6]="EXPECT_ARGUMENT_STYLE",e[e.INVALID_NUMBER_SKELETON=7]="INVALID_NUMBER_SKELETON",e[e.INVALID_DATE_TIME_SKELETON=8]="INVALID_DATE_TIME_SKELETON",e[e.EXPECT_NUMBER_SKELETON=9]="EXPECT_NUMBER_SKELETON",e[e.EXPECT_DATE_TIME_SKELETON=10]="EXPECT_DATE_TIME_SKELETON",e[e.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE=11]="UNCLOSED_QUOTE_IN_ARGUMENT_STYLE",e[e.EXPECT_SELECT_ARGUMENT_OPTIONS=12]="EXPECT_SELECT_ARGUMENT_OPTIONS",e[e.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE=13]="EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE=14]="INVALID_PLURAL_ARGUMENT_OFFSET_VALUE",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR=15]="EXPECT_SELECT_ARGUMENT_SELECTOR",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR=16]="EXPECT_PLURAL_ARGUMENT_SELECTOR",e[e.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT=17]="EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT",e[e.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT=18]="EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT",e[e.INVALID_PLURAL_ARGUMENT_SELECTOR=19]="INVALID_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_PLURAL_ARGUMENT_SELECTOR=20]="DUPLICATE_PLURAL_ARGUMENT_SELECTOR",e[e.DUPLICATE_SELECT_ARGUMENT_SELECTOR=21]="DUPLICATE_SELECT_ARGUMENT_SELECTOR",e[e.MISSING_OTHER_CLAUSE=22]="MISSING_OTHER_CLAUSE",e[e.INVALID_TAG=23]="INVALID_TAG",e[e.INVALID_TAG_NAME=25]="INVALID_TAG_NAME",e[e.UNMATCHED_CLOSING_TAG=26]="UNMATCHED_CLOSING_TAG",e[e.UNCLOSED_TAG=27]="UNCLOSED_TAG";}(cn||(cn={})),function(e){e[e.literal=0]="literal",e[e.argument=1]="argument",e[e.number=2]="number",e[e.date=3]="date",e[e.time=4]="time",e[e.select=5]="select",e[e.plural=6]="plural",e[e.pound=7]="pound",e[e.tag=8]="tag";}(pn||(pn={})),function(e){e[e.number=0]="number",e[e.dateTime=1]="dateTime";}(hn||(hn={}));var An=/[ \xA0\u1680\u2000-\u200A\u202F\u205F\u3000]/,Mn=/(?:[Eec]{1,6}|G{1,5}|[Qq]{1,5}|(?:[yYur]+|U{1,5})|[ML]{1,5}|d{1,2}|D{1,3}|F{1}|[abB]{1,5}|[hkHK]{1,2}|w{1,2}|W{1}|m{1,2}|s{1,2}|[zZOvVxX]{1,4})(?=([^']*'[^']*')*[^']*$)/g;function En(e){var t={};return e.replace(Mn,function(e){var a=e.length;switch(e[0]){case"G":t.era=4===a?"long":5===a?"narrow":"short";break;case"y":t.year=2===a?"2-digit":"numeric";break;case"Y":case"u":case"U":case"r":throw new RangeError("`Y/u/U/r` (year) patterns are not supported, use `y` instead");case"q":case"Q":throw new RangeError("`q/Q` (quarter) patterns are not supported");case"M":case"L":t.month=["numeric","2-digit","short","long","narrow"][a-1];break;case"w":case"W":throw new RangeError("`w/W` (week) patterns are not supported");case"d":t.day=["numeric","2-digit"][a-1];break;case"D":case"F":case"g":throw new RangeError("`D/F/g` (day) patterns are not supported, use `d` instead");case"E":t.weekday=4===a?"long":5===a?"narrow":"short";break;case"e":if(a<4)throw new RangeError("`e..eee` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][a-4];break;case"c":if(a<4)throw new RangeError("`c..ccc` (weekday) patterns are not supported");t.weekday=["short","long","narrow","short"][a-4];break;case"a":t.hour12=!0;break;case"b":case"B":throw new RangeError("`b/B` (period) patterns are not supported, use `a` instead");case"h":t.hourCycle="h12",t.hour=["numeric","2-digit"][a-1];break;case"H":t.hourCycle="h23",t.hour=["numeric","2-digit"][a-1];break;case"K":t.hourCycle="h11",t.hour=["numeric","2-digit"][a-1];break;case"k":t.hourCycle="h24",t.hour=["numeric","2-digit"][a-1];break;case"j":case"J":case"C":throw new RangeError("`j/J/C` (hour) patterns are not supported, use `h/H/K/k` instead");case"m":t.minute=["numeric","2-digit"][a-1];break;case"s":t.second=["numeric","2-digit"][a-1];break;case"S":case"A":throw new RangeError("`S/A` (second) patterns are not supported, use `s` instead");case"z":t.timeZoneName=a<4?"short":"long";break;case"Z":case"O":case"v":case"V":case"X":case"x":throw new RangeError("`Z/O/v/V/X/x` (timeZone) patterns are not supported, use `z` instead");}return"";}),t;}var Tn=/[\t-\r \x85\u200E\u200F\u2028\u2029]/i;var Dn=/^\.(?:(0+)(\*)?|(#+)|(0+)(#+))$/g,jn=/^(@+)?(\+|#+)?[rs]?$/g,On=/(\*)(0+)|(#+)(0+)|(0+)/g,Cn=/^(0+)$/;function Pn(e){var t={};return"r"===e[e.length-1]?t.roundingPriority="morePrecision":"s"===e[e.length-1]&&(t.roundingPriority="lessPrecision"),e.replace(jn,function(e,a,i){return"string"!=typeof i?(t.minimumSignificantDigits=a.length,t.maximumSignificantDigits=a.length):"+"===i?t.minimumSignificantDigits=a.length:"#"===a[0]?t.maximumSignificantDigits=a.length:(t.minimumSignificantDigits=a.length,t.maximumSignificantDigits=a.length+("string"==typeof i?i.length:0)),"";}),t;}function Nn(e){switch(e){case"sign-auto":return{signDisplay:"auto"};case"sign-accounting":case"()":return{currencySign:"accounting"};case"sign-always":case"+!":return{signDisplay:"always"};case"sign-accounting-always":case"()!":return{signDisplay:"always",currencySign:"accounting"};case"sign-except-zero":case"+?":return{signDisplay:"exceptZero"};case"sign-accounting-except-zero":case"()?":return{signDisplay:"exceptZero",currencySign:"accounting"};case"sign-never":case"+_":return{signDisplay:"never"};}}function Hn(e){var t;if("E"===e[0]&&"E"===e[1]?(t={notation:"engineering"},e=e.slice(2)):"E"===e[0]&&(t={notation:"scientific"},e=e.slice(1)),t){var a=e.slice(0,2);if("+!"===a?(t.signDisplay="always",e=e.slice(2)):"+?"===a&&(t.signDisplay="exceptZero",e=e.slice(2)),!Cn.test(e))throw new Error("Malformed concise eng/scientific notation");t.minimumIntegerDigits=e.length;}return t;}function In(e){var t=Nn(e);return t||{};}function Ln(e){for(var t={},a=0,n=e;a<n.length;a++){var s=n[a];switch(s.stem){case"percent":case"%":t.style="percent";continue;case"%x100":t.style="percent",t.scale=100;continue;case"currency":t.style="currency",t.currency=s.options[0];continue;case"group-off":case",_":t.useGrouping=!1;continue;case"precision-integer":case".":t.maximumFractionDigits=0;continue;case"measure-unit":case"unit":t.style="unit",t.unit=s.options[0].replace(/^(.*?)-/,"");continue;case"compact-short":case"K":t.notation="compact",t.compactDisplay="short";continue;case"compact-long":case"KK":t.notation="compact",t.compactDisplay="long";continue;case"scientific":t=i(i(i({},t),{notation:"scientific"}),s.options.reduce(function(e,t){return i(i({},e),In(t));},{}));continue;case"engineering":t=i(i(i({},t),{notation:"engineering"}),s.options.reduce(function(e,t){return i(i({},e),In(t));},{}));continue;case"notation-simple":t.notation="standard";continue;case"unit-width-narrow":t.currencyDisplay="narrowSymbol",t.unitDisplay="narrow";continue;case"unit-width-short":t.currencyDisplay="code",t.unitDisplay="short";continue;case"unit-width-full-name":t.currencyDisplay="name",t.unitDisplay="long";continue;case"unit-width-iso-code":t.currencyDisplay="symbol";continue;case"scale":t.scale=parseFloat(s.options[0]);continue;case"rounding-mode-floor":t.roundingMode="floor";continue;case"rounding-mode-ceiling":t.roundingMode="ceil";continue;case"rounding-mode-down":t.roundingMode="trunc";continue;case"rounding-mode-up":t.roundingMode="expand";continue;case"rounding-mode-half-even":t.roundingMode="halfEven";continue;case"rounding-mode-half-down":t.roundingMode="halfTrunc";continue;case"rounding-mode-half-up":t.roundingMode="halfExpand";continue;case"integer-width":if(s.options.length>1)throw new RangeError("integer-width stems only accept a single optional option");s.options[0].replace(On,function(e,a,i,n,s,r){if(a)t.minimumIntegerDigits=i.length;else{if(n&&s)throw new Error("We currently do not support maximum integer digits");if(r)throw new Error("We currently do not support exact integer digits");}return"";});continue;}if(Cn.test(s.stem))t.minimumIntegerDigits=s.stem.length;else if(Dn.test(s.stem)){if(s.options.length>1)throw new RangeError("Fraction-precision stems only accept a single optional option");s.stem.replace(Dn,function(e,a,i,n,s,r){return"*"===i?t.minimumFractionDigits=a.length:n&&"#"===n[0]?t.maximumFractionDigits=n.length:s&&r?(t.minimumFractionDigits=s.length,t.maximumFractionDigits=s.length+r.length):(t.minimumFractionDigits=a.length,t.maximumFractionDigits=a.length),"";});var r=s.options[0];"w"===r?t=i(i({},t),{trailingZeroDisplay:"stripIfInteger"}):r&&(t=i(i({},t),Pn(r)));}else if(jn.test(s.stem))t=i(i({},t),Pn(s.stem));else{var o=Nn(s.stem);o&&(t=i(i({},t),o));var l=Hn(s.stem);l&&(t=i(i({},t),l));}}return t;}var Bn,Un={"001":["H","h"],419:["h","H","hB","hb"],AC:["H","h","hb","hB"],AD:["H","hB"],AE:["h","hB","hb","H"],AF:["H","hb","hB","h"],AG:["h","hb","H","hB"],AI:["H","h","hb","hB"],AL:["h","H","hB"],AM:["H","hB"],AO:["H","hB"],AR:["h","H","hB","hb"],AS:["h","H"],AT:["H","hB"],AU:["h","hb","H","hB"],AW:["H","hB"],AX:["H"],AZ:["H","hB","h"],BA:["H","hB","h"],BB:["h","hb","H","hB"],BD:["h","hB","H"],BE:["H","hB"],BF:["H","hB"],BG:["H","hB","h"],BH:["h","hB","hb","H"],BI:["H","h"],BJ:["H","hB"],BL:["H","hB"],BM:["h","hb","H","hB"],BN:["hb","hB","h","H"],BO:["h","H","hB","hb"],BQ:["H"],BR:["H","hB"],BS:["h","hb","H","hB"],BT:["h","H"],BW:["H","h","hb","hB"],BY:["H","h"],BZ:["H","h","hb","hB"],CA:["h","hb","H","hB"],CC:["H","h","hb","hB"],CD:["hB","H"],CF:["H","h","hB"],CG:["H","hB"],CH:["H","hB","h"],CI:["H","hB"],CK:["H","h","hb","hB"],CL:["h","H","hB","hb"],CM:["H","h","hB"],CN:["H","hB","hb","h"],CO:["h","H","hB","hb"],CP:["H"],CR:["h","H","hB","hb"],CU:["h","H","hB","hb"],CV:["H","hB"],CW:["H","hB"],CX:["H","h","hb","hB"],CY:["h","H","hb","hB"],CZ:["H"],DE:["H","hB"],DG:["H","h","hb","hB"],DJ:["h","H"],DK:["H"],DM:["h","hb","H","hB"],DO:["h","H","hB","hb"],DZ:["h","hB","hb","H"],EA:["H","h","hB","hb"],EC:["h","H","hB","hb"],EE:["H","hB"],EG:["h","hB","hb","H"],EH:["h","hB","hb","H"],ER:["h","H"],ES:["H","hB","h","hb"],ET:["hB","hb","h","H"],FI:["H"],FJ:["h","hb","H","hB"],FK:["H","h","hb","hB"],FM:["h","hb","H","hB"],FO:["H","h"],FR:["H","hB"],GA:["H","hB"],GB:["H","h","hb","hB"],GD:["h","hb","H","hB"],GE:["H","hB","h"],GF:["H","hB"],GG:["H","h","hb","hB"],GH:["h","H"],GI:["H","h","hb","hB"],GL:["H","h"],GM:["h","hb","H","hB"],GN:["H","hB"],GP:["H","hB"],GQ:["H","hB","h","hb"],GR:["h","H","hb","hB"],GT:["h","H","hB","hb"],GU:["h","hb","H","hB"],GW:["H","hB"],GY:["h","hb","H","hB"],HK:["h","hB","hb","H"],HN:["h","H","hB","hb"],HR:["H","hB"],HU:["H","h"],IC:["H","h","hB","hb"],ID:["H"],IE:["H","h","hb","hB"],IL:["H","hB"],IM:["H","h","hb","hB"],IN:["h","H"],IO:["H","h","hb","hB"],IQ:["h","hB","hb","H"],IR:["hB","H"],IS:["H"],IT:["H","hB"],JE:["H","h","hb","hB"],JM:["h","hb","H","hB"],JO:["h","hB","hb","H"],JP:["H","K","h"],KE:["hB","hb","H","h"],KG:["H","h","hB","hb"],KH:["hB","h","H","hb"],KI:["h","hb","H","hB"],KM:["H","h","hB","hb"],KN:["h","hb","H","hB"],KP:["h","H","hB","hb"],KR:["h","H","hB","hb"],KW:["h","hB","hb","H"],KY:["h","hb","H","hB"],KZ:["H","hB"],LA:["H","hb","hB","h"],LB:["h","hB","hb","H"],LC:["h","hb","H","hB"],LI:["H","hB","h"],LK:["H","h","hB","hb"],LR:["h","hb","H","hB"],LS:["h","H"],LT:["H","h","hb","hB"],LU:["H","h","hB"],LV:["H","hB","hb","h"],LY:["h","hB","hb","H"],MA:["H","h","hB","hb"],MC:["H","hB"],MD:["H","hB"],ME:["H","hB","h"],MF:["H","hB"],MG:["H","h"],MH:["h","hb","H","hB"],MK:["H","h","hb","hB"],ML:["H"],MM:["hB","hb","H","h"],MN:["H","h","hb","hB"],MO:["h","hB","hb","H"],MP:["h","hb","H","hB"],MQ:["H","hB"],MR:["h","hB","hb","H"],MS:["H","h","hb","hB"],MT:["H","h"],MU:["H","h"],MV:["H","h"],MW:["h","hb","H","hB"],MX:["h","H","hB","hb"],MY:["hb","hB","h","H"],MZ:["H","hB"],NA:["h","H","hB","hb"],NC:["H","hB"],NE:["H"],NF:["H","h","hb","hB"],NG:["H","h","hb","hB"],NI:["h","H","hB","hb"],NL:["H","hB"],NO:["H","h"],NP:["H","h","hB"],NR:["H","h","hb","hB"],NU:["H","h","hb","hB"],NZ:["h","hb","H","hB"],OM:["h","hB","hb","H"],PA:["h","H","hB","hb"],PE:["h","H","hB","hb"],PF:["H","h","hB"],PG:["h","H"],PH:["h","hB","hb","H"],PK:["h","hB","H"],PL:["H","h"],PM:["H","hB"],PN:["H","h","hb","hB"],PR:["h","H","hB","hb"],PS:["h","hB","hb","H"],PT:["H","hB"],PW:["h","H"],PY:["h","H","hB","hb"],QA:["h","hB","hb","H"],RE:["H","hB"],RO:["H","hB"],RS:["H","hB","h"],RU:["H"],RW:["H","h"],SA:["h","hB","hb","H"],SB:["h","hb","H","hB"],SC:["H","h","hB"],SD:["h","hB","hb","H"],SE:["H"],SG:["h","hb","H","hB"],SH:["H","h","hb","hB"],SI:["H","hB"],SJ:["H"],SK:["H"],SL:["h","hb","H","hB"],SM:["H","h","hB"],SN:["H","h","hB"],SO:["h","H"],SR:["H","hB"],SS:["h","hb","H","hB"],ST:["H","hB"],SV:["h","H","hB","hb"],SX:["H","h","hb","hB"],SY:["h","hB","hb","H"],SZ:["h","hb","H","hB"],TA:["H","h","hb","hB"],TC:["h","hb","H","hB"],TD:["h","H","hB"],TF:["H","h","hB"],TG:["H","hB"],TH:["H","h"],TJ:["H","h"],TL:["H","hB","hb","h"],TM:["H","h"],TN:["h","hB","hb","H"],TO:["h","H"],TR:["H","hB"],TT:["h","hb","H","hB"],TW:["hB","hb","h","H"],TZ:["hB","hb","H","h"],UA:["H","hB","h"],UG:["hB","hb","H","h"],UM:["h","hb","H","hB"],US:["h","hb","H","hB"],UY:["h","H","hB","hb"],UZ:["H","hB","h"],VA:["H","h","hB"],VC:["h","hb","H","hB"],VE:["h","H","hB","hb"],VG:["h","hb","H","hB"],VI:["h","hb","H","hB"],VN:["H","h"],VU:["h","H"],WF:["H","hB"],WS:["h","H"],XK:["H","hB","h"],YE:["h","hB","hb","H"],YT:["H","hB"],ZA:["H","h","hb","hB"],ZM:["h","hb","H","hB"],ZW:["H","h"],"af-ZA":["H","h","hB","hb"],"ar-001":["h","hB","hb","H"],"ca-ES":["H","h","hB"],"en-001":["h","hb","H","hB"],"en-HK":["h","hb","H","hB"],"en-IL":["H","h","hb","hB"],"en-MY":["h","hb","H","hB"],"es-BR":["H","h","hB","hb"],"es-ES":["H","h","hB","hb"],"es-GQ":["H","h","hB","hb"],"fr-CA":["H","h","hB"],"gl-ES":["H","h","hB"],"gu-IN":["hB","hb","h","H"],"hi-IN":["hB","h","H"],"it-CH":["H","h","hB"],"it-IT":["H","h","hB"],"kn-IN":["hB","h","H"],"ml-IN":["hB","h","H"],"mr-IN":["hB","hb","h","H"],"pa-IN":["hB","hb","h","H"],"ta-IN":["hB","h","hb","H"],"te-IN":["hB","h","H"],"zu-ZA":["H","hB","hb","h"]};function Rn(e){var t=e.hourCycle;if(void 0===t&&e.hourCycles&&e.hourCycles.length&&(t=e.hourCycles[0]),t)switch(t){case"h24":return"k";case"h23":return"H";case"h12":return"h";case"h11":return"K";default:throw new Error("Invalid hourCycle");}var a,i=e.language;return"root"!==i&&(a=e.maximize().region),(Un[a||""]||Un[i||""]||Un["".concat(i,"-001")]||Un["001"])[0];}var Wn=new RegExp("^".concat(An.source,"*")),Fn=new RegExp("".concat(An.source,"*$"));function qn(e,t){return{start:e,end:t};}var Vn=!!String.prototype.startsWith&&"_a".startsWith("a",1),Zn=!!String.fromCodePoint,Yn=!!Object.fromEntries,Gn=!!String.prototype.codePointAt,Kn=!!String.prototype.trimStart,Xn=!!String.prototype.trimEnd,Jn=!!Number.isSafeInteger?Number.isSafeInteger:function(e){return"number"==typeof e&&isFinite(e)&&Math.floor(e)===e&&Math.abs(e)<=9007199254740991;},Qn=!0;try{Qn="a"===(null===(Bn=os("([^\\p{White_Space}\\p{Pattern_Syntax}]*)","yu").exec("a"))||void 0===Bn?void 0:Bn[0]);}catch(H){Qn=!1;}var es,ts=Vn?function(e,t,a){return e.startsWith(t,a);}:function(e,t,a){return e.slice(a,a+t.length)===t;},as=Zn?String.fromCodePoint:function(){for(var e=[],t=0;t<arguments.length;t++)e[t]=arguments[t];for(var a,i="",n=e.length,s=0;n>s;){if((a=e[s++])>1114111)throw RangeError(a+" is not a valid code point");i+=a<65536?String.fromCharCode(a):String.fromCharCode(55296+((a-=65536)>>10),a%1024+56320);}return i;},is=Yn?Object.fromEntries:function(e){for(var t={},a=0,i=e;a<i.length;a++){var n=i[a],s=n[0],r=n[1];t[s]=r;}return t;},ns=Gn?function(e,t){return e.codePointAt(t);}:function(e,t){var a=e.length;if(!(t<0||t>=a)){var i,n=e.charCodeAt(t);return n<55296||n>56319||t+1===a||(i=e.charCodeAt(t+1))<56320||i>57343?n:i-56320+(n-55296<<10)+65536;}},ss=Kn?function(e){return e.trimStart();}:function(e){return e.replace(Wn,"");},rs=Xn?function(e){return e.trimEnd();}:function(e){return e.replace(Fn,"");};function os(e,t){return new RegExp(e,t);}if(Qn){var ls=os("([^\\p{White_Space}\\p{Pattern_Syntax}]*)","yu");es=function(e,t){var a;return ls.lastIndex=t,null!==(a=ls.exec(e)[1])&&void 0!==a?a:"";};}else es=function(e,t){for(var a=[];;){var i=ns(e,t);if(void 0===i||hs(i)||gs(i))break;a.push(i),t+=i>=65536?2:1;}return as.apply(void 0,a);};var ds,us=function(){function e(e,t){void 0===t&&(t={}),this.message=e,this.position={offset:0,line:1,column:1},this.ignoreTag=!!t.ignoreTag,this.locale=t.locale,this.requiresOtherClause=!!t.requiresOtherClause,this.shouldParseSkeletons=!!t.shouldParseSkeletons;}return e.prototype.parse=function(){if(0!==this.offset())throw Error("parser can only be used once");return this.parseMessage(0,"",!1);},e.prototype.parseMessage=function(e,t,a){for(var i=[];!this.isEOF();){var n=this.char();if(123===n){if((s=this.parseArgument(e,a)).err)return s;i.push(s.val);}else{if(125===n&&e>0)break;if(35!==n||"plural"!==t&&"selectordinal"!==t){if(60===n&&!this.ignoreTag&&47===this.peek()){if(a)break;return this.error(cn.UNMATCHED_CLOSING_TAG,qn(this.clonePosition(),this.clonePosition()));}if(60===n&&!this.ignoreTag&&cs(this.peek()||0)){if((s=this.parseTag(e,t)).err)return s;i.push(s.val);}else{var s;if((s=this.parseLiteral(e,t)).err)return s;i.push(s.val);}}else{var r=this.clonePosition();this.bump(),i.push({type:pn.pound,location:qn(r,this.clonePosition())});}}}return{val:i,err:null};},e.prototype.parseTag=function(e,t){var a=this.clonePosition();this.bump();var i=this.parseTagName();if(this.bumpSpace(),this.bumpIf("/>"))return{val:{type:pn.literal,value:"<".concat(i,"/>"),location:qn(a,this.clonePosition())},err:null};if(this.bumpIf(">")){var n=this.parseMessage(e+1,t,!0);if(n.err)return n;var s=n.val,r=this.clonePosition();if(this.bumpIf("</")){if(this.isEOF()||!cs(this.char()))return this.error(cn.INVALID_TAG,qn(r,this.clonePosition()));var o=this.clonePosition();return i!==this.parseTagName()?this.error(cn.UNMATCHED_CLOSING_TAG,qn(o,this.clonePosition())):(this.bumpSpace(),this.bumpIf(">")?{val:{type:pn.tag,value:i,children:s,location:qn(a,this.clonePosition())},err:null}:this.error(cn.INVALID_TAG,qn(r,this.clonePosition())));}return this.error(cn.UNCLOSED_TAG,qn(a,this.clonePosition()));}return this.error(cn.INVALID_TAG,qn(a,this.clonePosition()));},e.prototype.parseTagName=function(){var e=this.offset();for(this.bump();!this.isEOF()&&ps(this.char());)this.bump();return this.message.slice(e,this.offset());},e.prototype.parseLiteral=function(e,t){for(var a=this.clonePosition(),i="";;){var n=this.tryParseQuote(t);if(n)i+=n;else{var s=this.tryParseUnquoted(e,t);if(s)i+=s;else{var r=this.tryParseLeftAngleBracket();if(!r)break;i+=r;}}}var o=qn(a,this.clonePosition());return{val:{type:pn.literal,value:i,location:o},err:null};},e.prototype.tryParseLeftAngleBracket=function(){return this.isEOF()||60!==this.char()||!this.ignoreTag&&(cs(e=this.peek()||0)||47===e)?null:(this.bump(),"<");var e;},e.prototype.tryParseQuote=function(e){if(this.isEOF()||39!==this.char())return null;switch(this.peek()){case 39:return this.bump(),this.bump(),"'";case 123:case 60:case 62:case 125:break;case 35:if("plural"===e||"selectordinal"===e)break;return null;default:return null;}this.bump();var t=[this.char()];for(this.bump();!this.isEOF();){var a=this.char();if(39===a){if(39!==this.peek()){this.bump();break;}t.push(39),this.bump();}else t.push(a);this.bump();}return as.apply(void 0,t);},e.prototype.tryParseUnquoted=function(e,t){if(this.isEOF())return null;var a=this.char();return 60===a||123===a||35===a&&("plural"===t||"selectordinal"===t)||125===a&&e>0?null:(this.bump(),as(a));},e.prototype.parseArgument=function(e,t){var a=this.clonePosition();if(this.bump(),this.bumpSpace(),this.isEOF())return this.error(cn.EXPECT_ARGUMENT_CLOSING_BRACE,qn(a,this.clonePosition()));if(125===this.char())return this.bump(),this.error(cn.EMPTY_ARGUMENT,qn(a,this.clonePosition()));var i=this.parseIdentifierIfPossible().value;if(!i)return this.error(cn.MALFORMED_ARGUMENT,qn(a,this.clonePosition()));if(this.bumpSpace(),this.isEOF())return this.error(cn.EXPECT_ARGUMENT_CLOSING_BRACE,qn(a,this.clonePosition()));switch(this.char()){case 125:return this.bump(),{val:{type:pn.argument,value:i,location:qn(a,this.clonePosition())},err:null};case 44:return this.bump(),this.bumpSpace(),this.isEOF()?this.error(cn.EXPECT_ARGUMENT_CLOSING_BRACE,qn(a,this.clonePosition())):this.parseArgumentOptions(e,t,i,a);default:return this.error(cn.MALFORMED_ARGUMENT,qn(a,this.clonePosition()));}},e.prototype.parseIdentifierIfPossible=function(){var e=this.clonePosition(),t=this.offset(),a=es(this.message,t),i=t+a.length;return this.bumpTo(i),{value:a,location:qn(e,this.clonePosition())};},e.prototype.parseArgumentOptions=function(e,t,a,n){var s,r=this.clonePosition(),o=this.parseIdentifierIfPossible().value,l=this.clonePosition();switch(o){case"":return this.error(cn.EXPECT_ARGUMENT_TYPE,qn(r,l));case"number":case"date":case"time":this.bumpSpace();var d=null;if(this.bumpIf(",")){this.bumpSpace();var u=this.clonePosition();if((_=this.parseSimpleArgStyleIfPossible()).err)return _;if(0===(g=rs(_.val)).length)return this.error(cn.EXPECT_ARGUMENT_STYLE,qn(this.clonePosition(),this.clonePosition()));d={style:g,styleLocation:qn(u,this.clonePosition())};}if((b=this.tryParseArgumentClose(n)).err)return b;var c=qn(n,this.clonePosition());if(d&&ts(null==d?void 0:d.style,"::",0)){var p=ss(d.style.slice(2));if("number"===o)return(_=this.parseNumberSkeletonFromString(p,d.styleLocation)).err?_:{val:{type:pn.number,value:a,location:c,style:_.val},err:null};if(0===p.length)return this.error(cn.EXPECT_DATE_TIME_SKELETON,c);var h=p;this.locale&&(h=function(e,t){for(var a="",i=0;i<e.length;i++){var n=e.charAt(i);if("j"===n){for(var s=0;i+1<e.length&&e.charAt(i+1)===n;)s++,i++;var r=1+(1&s),o=s<2?1:3+(s>>1),l=Rn(t);for("H"!=l&&"k"!=l||(o=0);o-->0;)a+="a";for(;r-->0;)a=l+a;}else a+="J"===n?"H":n;}return a;}(p,this.locale));var g={type:hn.dateTime,pattern:h,location:d.styleLocation,parsedOptions:this.shouldParseSkeletons?En(h):{}};return{val:{type:"date"===o?pn.date:pn.time,value:a,location:c,style:g},err:null};}return{val:{type:"number"===o?pn.number:"date"===o?pn.date:pn.time,value:a,location:c,style:null!==(s=null==d?void 0:d.style)&&void 0!==s?s:null},err:null};case"plural":case"selectordinal":case"select":var m=this.clonePosition();if(this.bumpSpace(),!this.bumpIf(","))return this.error(cn.EXPECT_SELECT_ARGUMENT_OPTIONS,qn(m,i({},m)));this.bumpSpace();var v=this.parseIdentifierIfPossible(),f=0;if("select"!==o&&"offset"===v.value){if(!this.bumpIf(":"))return this.error(cn.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE,qn(this.clonePosition(),this.clonePosition()));var _;if(this.bumpSpace(),(_=this.tryParseDecimalInteger(cn.EXPECT_PLURAL_ARGUMENT_OFFSET_VALUE,cn.INVALID_PLURAL_ARGUMENT_OFFSET_VALUE)).err)return _;this.bumpSpace(),v=this.parseIdentifierIfPossible(),f=_.val;}var b,y=this.tryParsePluralOrSelectOptions(e,o,t,v);if(y.err)return y;if((b=this.tryParseArgumentClose(n)).err)return b;var w=qn(n,this.clonePosition());return"select"===o?{val:{type:pn.select,value:a,options:is(y.val),location:w},err:null}:{val:{type:pn.plural,value:a,options:is(y.val),offset:f,pluralType:"plural"===o?"cardinal":"ordinal",location:w},err:null};default:return this.error(cn.INVALID_ARGUMENT_TYPE,qn(r,l));}},e.prototype.tryParseArgumentClose=function(e){return this.isEOF()||125!==this.char()?this.error(cn.EXPECT_ARGUMENT_CLOSING_BRACE,qn(e,this.clonePosition())):(this.bump(),{val:!0,err:null});},e.prototype.parseSimpleArgStyleIfPossible=function(){for(var e=0,t=this.clonePosition();!this.isEOF();){switch(this.char()){case 39:this.bump();var a=this.clonePosition();if(!this.bumpUntil("'"))return this.error(cn.UNCLOSED_QUOTE_IN_ARGUMENT_STYLE,qn(a,this.clonePosition()));this.bump();break;case 123:e+=1,this.bump();break;case 125:if(!(e>0))return{val:this.message.slice(t.offset,this.offset()),err:null};e-=1;break;default:this.bump();}}return{val:this.message.slice(t.offset,this.offset()),err:null};},e.prototype.parseNumberSkeletonFromString=function(e,t){var a=[];try{a=function(e){if(0===e.length)throw new Error("Number skeleton cannot be empty");for(var t=e.split(Tn).filter(function(e){return e.length>0;}),a=[],i=0,n=t;i<n.length;i++){var s=n[i].split("/");if(0===s.length)throw new Error("Invalid number skeleton");for(var r=s[0],o=s.slice(1),l=0,d=o;l<d.length;l++)if(0===d[l].length)throw new Error("Invalid number skeleton");a.push({stem:r,options:o});}return a;}(e);}catch(e){return this.error(cn.INVALID_NUMBER_SKELETON,t);}return{val:{type:hn.number,tokens:a,location:t,parsedOptions:this.shouldParseSkeletons?Ln(a):{}},err:null};},e.prototype.tryParsePluralOrSelectOptions=function(e,t,a,i){for(var n,s=!1,r=[],o=new Set(),l=i.value,d=i.location;;){if(0===l.length){var u=this.clonePosition();if("select"===t||!this.bumpIf("="))break;var c=this.tryParseDecimalInteger(cn.EXPECT_PLURAL_ARGUMENT_SELECTOR,cn.INVALID_PLURAL_ARGUMENT_SELECTOR);if(c.err)return c;d=qn(u,this.clonePosition()),l=this.message.slice(u.offset,this.offset());}if(o.has(l))return this.error("select"===t?cn.DUPLICATE_SELECT_ARGUMENT_SELECTOR:cn.DUPLICATE_PLURAL_ARGUMENT_SELECTOR,d);"other"===l&&(s=!0),this.bumpSpace();var p=this.clonePosition();if(!this.bumpIf("{"))return this.error("select"===t?cn.EXPECT_SELECT_ARGUMENT_SELECTOR_FRAGMENT:cn.EXPECT_PLURAL_ARGUMENT_SELECTOR_FRAGMENT,qn(this.clonePosition(),this.clonePosition()));var h=this.parseMessage(e+1,t,a);if(h.err)return h;var g=this.tryParseArgumentClose(p);if(g.err)return g;r.push([l,{value:h.val,location:qn(p,this.clonePosition())}]),o.add(l),this.bumpSpace(),l=(n=this.parseIdentifierIfPossible()).value,d=n.location;}return 0===r.length?this.error("select"===t?cn.EXPECT_SELECT_ARGUMENT_SELECTOR:cn.EXPECT_PLURAL_ARGUMENT_SELECTOR,qn(this.clonePosition(),this.clonePosition())):this.requiresOtherClause&&!s?this.error(cn.MISSING_OTHER_CLAUSE,qn(this.clonePosition(),this.clonePosition())):{val:r,err:null};},e.prototype.tryParseDecimalInteger=function(e,t){var a=1,i=this.clonePosition();this.bumpIf("+")||this.bumpIf("-")&&(a=-1);for(var n=!1,s=0;!this.isEOF();){var r=this.char();if(!(r>=48&&r<=57))break;n=!0,s=10*s+(r-48),this.bump();}var o=qn(i,this.clonePosition());return n?Jn(s*=a)?{val:s,err:null}:this.error(t,o):this.error(e,o);},e.prototype.offset=function(){return this.position.offset;},e.prototype.isEOF=function(){return this.offset()===this.message.length;},e.prototype.clonePosition=function(){return{offset:this.position.offset,line:this.position.line,column:this.position.column};},e.prototype.char=function(){var e=this.position.offset;if(e>=this.message.length)throw Error("out of bound");var t=ns(this.message,e);if(void 0===t)throw Error("Offset ".concat(e," is at invalid UTF-16 code unit boundary"));return t;},e.prototype.error=function(e,t){return{val:null,err:{kind:e,message:this.message,location:t}};},e.prototype.bump=function(){if(!this.isEOF()){var e=this.char();10===e?(this.position.line+=1,this.position.column=1,this.position.offset+=1):(this.position.column+=1,this.position.offset+=e<65536?1:2);}},e.prototype.bumpIf=function(e){if(ts(this.message,e,this.offset())){for(var t=0;t<e.length;t++)this.bump();return!0;}return!1;},e.prototype.bumpUntil=function(e){var t=this.offset(),a=this.message.indexOf(e,t);return a>=0?(this.bumpTo(a),!0):(this.bumpTo(this.message.length),!1);},e.prototype.bumpTo=function(e){if(this.offset()>e)throw Error("targetOffset ".concat(e," must be greater than or equal to the current offset ").concat(this.offset()));for(e=Math.min(e,this.message.length);;){var t=this.offset();if(t===e)break;if(t>e)throw Error("targetOffset ".concat(e," is at invalid UTF-16 code unit boundary"));if(this.bump(),this.isEOF())break;}},e.prototype.bumpSpace=function(){for(;!this.isEOF()&&hs(this.char());)this.bump();},e.prototype.peek=function(){if(this.isEOF())return null;var e=this.char(),t=this.offset(),a=this.message.charCodeAt(t+(e>=65536?2:1));return null!=a?a:null;},e;}();function cs(e){return e>=97&&e<=122||e>=65&&e<=90;}function ps(e){return 45===e||46===e||e>=48&&e<=57||95===e||e>=97&&e<=122||e>=65&&e<=90||183==e||e>=192&&e<=214||e>=216&&e<=246||e>=248&&e<=893||e>=895&&e<=8191||e>=8204&&e<=8205||e>=8255&&e<=8256||e>=8304&&e<=8591||e>=11264&&e<=12271||e>=12289&&e<=55295||e>=63744&&e<=64975||e>=65008&&e<=65533||e>=65536&&e<=983039;}function hs(e){return e>=9&&e<=13||32===e||133===e||e>=8206&&e<=8207||8232===e||8233===e;}function gs(e){return e>=33&&e<=35||36===e||e>=37&&e<=39||40===e||41===e||42===e||43===e||44===e||45===e||e>=46&&e<=47||e>=58&&e<=59||e>=60&&e<=62||e>=63&&e<=64||91===e||92===e||93===e||94===e||96===e||123===e||124===e||125===e||126===e||161===e||e>=162&&e<=165||166===e||167===e||169===e||171===e||172===e||174===e||176===e||177===e||182===e||187===e||191===e||215===e||247===e||e>=8208&&e<=8213||e>=8214&&e<=8215||8216===e||8217===e||8218===e||e>=8219&&e<=8220||8221===e||8222===e||8223===e||e>=8224&&e<=8231||e>=8240&&e<=8248||8249===e||8250===e||e>=8251&&e<=8254||e>=8257&&e<=8259||8260===e||8261===e||8262===e||e>=8263&&e<=8273||8274===e||8275===e||e>=8277&&e<=8286||e>=8592&&e<=8596||e>=8597&&e<=8601||e>=8602&&e<=8603||e>=8604&&e<=8607||8608===e||e>=8609&&e<=8610||8611===e||e>=8612&&e<=8613||8614===e||e>=8615&&e<=8621||8622===e||e>=8623&&e<=8653||e>=8654&&e<=8655||e>=8656&&e<=8657||8658===e||8659===e||8660===e||e>=8661&&e<=8691||e>=8692&&e<=8959||e>=8960&&e<=8967||8968===e||8969===e||8970===e||8971===e||e>=8972&&e<=8991||e>=8992&&e<=8993||e>=8994&&e<=9e3||9001===e||9002===e||e>=9003&&e<=9083||9084===e||e>=9085&&e<=9114||e>=9115&&e<=9139||e>=9140&&e<=9179||e>=9180&&e<=9185||e>=9186&&e<=9254||e>=9255&&e<=9279||e>=9280&&e<=9290||e>=9291&&e<=9311||e>=9472&&e<=9654||9655===e||e>=9656&&e<=9664||9665===e||e>=9666&&e<=9719||e>=9720&&e<=9727||e>=9728&&e<=9838||9839===e||e>=9840&&e<=10087||10088===e||10089===e||10090===e||10091===e||10092===e||10093===e||10094===e||10095===e||10096===e||10097===e||10098===e||10099===e||10100===e||10101===e||e>=10132&&e<=10175||e>=10176&&e<=10180||10181===e||10182===e||e>=10183&&e<=10213||10214===e||10215===e||10216===e||10217===e||10218===e||10219===e||10220===e||10221===e||10222===e||10223===e||e>=10224&&e<=10239||e>=10240&&e<=10495||e>=10496&&e<=10626||10627===e||10628===e||10629===e||10630===e||10631===e||10632===e||10633===e||10634===e||10635===e||10636===e||10637===e||10638===e||10639===e||10640===e||10641===e||10642===e||10643===e||10644===e||10645===e||10646===e||10647===e||10648===e||e>=10649&&e<=10711||10712===e||10713===e||10714===e||10715===e||e>=10716&&e<=10747||10748===e||10749===e||e>=10750&&e<=11007||e>=11008&&e<=11055||e>=11056&&e<=11076||e>=11077&&e<=11078||e>=11079&&e<=11084||e>=11085&&e<=11123||e>=11124&&e<=11125||e>=11126&&e<=11157||11158===e||e>=11159&&e<=11263||e>=11776&&e<=11777||11778===e||11779===e||11780===e||11781===e||e>=11782&&e<=11784||11785===e||11786===e||11787===e||11788===e||11789===e||e>=11790&&e<=11798||11799===e||e>=11800&&e<=11801||11802===e||11803===e||11804===e||11805===e||e>=11806&&e<=11807||11808===e||11809===e||11810===e||11811===e||11812===e||11813===e||11814===e||11815===e||11816===e||11817===e||e>=11818&&e<=11822||11823===e||e>=11824&&e<=11833||e>=11834&&e<=11835||e>=11836&&e<=11839||11840===e||11841===e||11842===e||e>=11843&&e<=11855||e>=11856&&e<=11857||11858===e||e>=11859&&e<=11903||e>=12289&&e<=12291||12296===e||12297===e||12298===e||12299===e||12300===e||12301===e||12302===e||12303===e||12304===e||12305===e||e>=12306&&e<=12307||12308===e||12309===e||12310===e||12311===e||12312===e||12313===e||12314===e||12315===e||12316===e||12317===e||e>=12318&&e<=12319||12320===e||12336===e||64830===e||64831===e||e>=65093&&e<=65094;}function ms(e){e.forEach(function(e){if(delete e.location,wn(e)||kn(e))for(var t in e.options)delete e.options[t].location,ms(e.options[t].value);else _n(e)&&xn(e.style)||(bn(e)||yn(e))&&$n(e.style)?delete e.style.location:Sn(e)&&ms(e.children);});}function vs(e,t){void 0===t&&(t={}),t=i({shouldParseSkeletons:!0,requiresOtherClause:!0},t);var a=new us(e,t).parse();if(a.err){var n=SyntaxError(cn[a.err.kind]);throw n.location=a.err.location,n.originalMessage=a.err.message,n;}return(null==t?void 0:t.captureLocation)||ms(a.val),a.val;}!function(e){e.MISSING_VALUE="MISSING_VALUE",e.INVALID_VALUE="INVALID_VALUE",e.MISSING_INTL_API="MISSING_INTL_API";}(ds||(ds={}));var fs,_s=function(e){function t(t,a,i){var n=e.call(this,t)||this;return n.code=a,n.originalMessage=i,n;}return a(t,e),t.prototype.toString=function(){return"[formatjs Error: ".concat(this.code,"] ").concat(this.message);},t;}(Error),bs=function(e){function t(t,a,i,n){return e.call(this,'Invalid values for "'.concat(t,'": "').concat(a,'". Options are "').concat(Object.keys(i).join('", "'),'"'),ds.INVALID_VALUE,n)||this;}return a(t,e),t;}(_s),ys=function(e){function t(t,a,i){return e.call(this,'Value for "'.concat(t,'" must be of type ').concat(a),ds.INVALID_VALUE,i)||this;}return a(t,e),t;}(_s),ws=function(e){function t(t,a){return e.call(this,'The intl string context variable "'.concat(t,'" was not provided to the string "').concat(a,'"'),ds.MISSING_VALUE,a)||this;}return a(t,e),t;}(_s);function ks(e){return"function"==typeof e;}function zs(e,t,a,i,n,s,r){if(1===e.length&&vn(e[0]))return[{type:fs.literal,value:e[0].value}];for(var o=[],l=0,d=e;l<d.length;l++){var u=d[l];if(vn(u))o.push({type:fs.literal,value:u.value});else if(zn(u))"number"==typeof s&&o.push({type:fs.literal,value:a.getNumberFormat(t).format(s)});else{var c=u.value;if(!n||!(c in n))throw new ws(c,r);var p=n[c];if(fn(u))p&&"string"!=typeof p&&"number"!=typeof p||(p="string"==typeof p||"number"==typeof p?String(p):""),o.push({type:"string"==typeof p?fs.literal:fs.object,value:p});else if(bn(u)){var h="string"==typeof u.style?i.date[u.style]:$n(u.style)?u.style.parsedOptions:void 0;o.push({type:fs.literal,value:a.getDateTimeFormat(t,h).format(p)});}else if(yn(u)){h="string"==typeof u.style?i.time[u.style]:$n(u.style)?u.style.parsedOptions:i.time.medium;o.push({type:fs.literal,value:a.getDateTimeFormat(t,h).format(p)});}else if(_n(u)){(h="string"==typeof u.style?i.number[u.style]:xn(u.style)?u.style.parsedOptions:void 0)&&h.scale&&(p*=h.scale||1),o.push({type:fs.literal,value:a.getNumberFormat(t,h).format(p)});}else{if(Sn(u)){var g=u.children,m=u.value,v=n[m];if(!ks(v))throw new ys(m,"function",r);var f=v(zs(g,t,a,i,n,s).map(function(e){return e.value;}));Array.isArray(f)||(f=[f]),o.push.apply(o,f.map(function(e){return{type:"string"==typeof e?fs.literal:fs.object,value:e};}));}if(wn(u)){if(!(_=u.options[p]||u.options.other))throw new bs(u.value,p,Object.keys(u.options),r);o.push.apply(o,zs(_.value,t,a,i,n));}else if(kn(u)){var _;if(!(_=u.options["=".concat(p)])){if(!Intl.PluralRules)throw new _s('Intl.PluralRules is not available in this environment.\nTry polyfilling it using "@formatjs/intl-pluralrules"\n',ds.MISSING_INTL_API,r);var b=a.getPluralRules(t,{type:u.pluralType}).select(p-(u.offset||0));_=u.options[b]||u.options.other;}if(!_)throw new bs(u.value,p,Object.keys(u.options),r);o.push.apply(o,zs(_.value,t,a,i,n,p-(u.offset||0)));}else;}}}return function(e){return e.length<2?e:e.reduce(function(e,t){var a=e[e.length-1];return a&&a.type===fs.literal&&t.type===fs.literal?a.value+=t.value:e.push(t),e;},[]);}(o);}function Ss(e,t){return t?Object.keys(e).reduce(function(a,n){var s,r;return a[n]=(s=e[n],(r=t[n])?i(i(i({},s||{}),r||{}),Object.keys(s).reduce(function(e,t){return e[t]=i(i({},s[t]),r[t]||{}),e;},{})):s),a;},i({},e)):e;}function xs(e){return{create:function(){return{get:function(t){return e[t];},set:function(t,a){e[t]=a;}};}};}!function(e){e[e.literal=0]="literal",e[e.object=1]="object";}(fs||(fs={}));var $s=function(){function e(t,a,n,r){void 0===a&&(a=e.defaultLocale);var o,l=this;if(this.formatterCache={number:{},dateTime:{},pluralRules:{}},this.format=function(e){var t=l.formatToParts(e);if(1===t.length)return t[0].value;var a=t.reduce(function(e,t){return e.length&&t.type===fs.literal&&"string"==typeof e[e.length-1]?e[e.length-1]+=t.value:e.push(t.value),e;},[]);return a.length<=1?a[0]||"":a;},this.formatToParts=function(e){return zs(l.ast,l.locales,l.formatters,l.formats,e,void 0,l.message);},this.resolvedOptions=function(){var e;return{locale:(null===(e=l.resolvedLocale)||void 0===e?void 0:e.toString())||Intl.NumberFormat.supportedLocalesOf(l.locales)[0]};},this.getAst=function(){return l.ast;},this.locales=a,this.resolvedLocale=e.resolveLocale(a),"string"==typeof t){if(this.message=t,!e.__parse)throw new TypeError("IntlMessageFormat.__parse must be set to process `message` of type `string`");var d=r||{};d.formatters;var u=function(e,t){var a={};for(var i in e)Object.prototype.hasOwnProperty.call(e,i)&&t.indexOf(i)<0&&(a[i]=e[i]);if(null!=e&&"function"==typeof Object.getOwnPropertySymbols){var n=0;for(i=Object.getOwnPropertySymbols(e);n<i.length;n++)t.indexOf(i[n])<0&&Object.prototype.propertyIsEnumerable.call(e,i[n])&&(a[i[n]]=e[i[n]]);}return a;}(d,["formatters"]);this.ast=e.__parse(t,i(i({},u),{locale:this.resolvedLocale}));}else this.ast=t;if(!Array.isArray(this.ast))throw new TypeError("A message must be provided as a String or AST.");this.formats=Ss(e.formats,n),this.formatters=r&&r.formatters||(void 0===(o=this.formatterCache)&&(o={number:{},dateTime:{},pluralRules:{}}),{getNumberFormat:nn(function(){for(var e,t=[],a=0;a<arguments.length;a++)t[a]=arguments[a];return new((e=Intl.NumberFormat).bind.apply(e,s([void 0],t,!1)))();},{cache:xs(o.number),strategy:mn.variadic}),getDateTimeFormat:nn(function(){for(var e,t=[],a=0;a<arguments.length;a++)t[a]=arguments[a];return new((e=Intl.DateTimeFormat).bind.apply(e,s([void 0],t,!1)))();},{cache:xs(o.dateTime),strategy:mn.variadic}),getPluralRules:nn(function(){for(var e,t=[],a=0;a<arguments.length;a++)t[a]=arguments[a];return new((e=Intl.PluralRules).bind.apply(e,s([void 0],t,!1)))();},{cache:xs(o.pluralRules),strategy:mn.variadic})});}return Object.defineProperty(e,"defaultLocale",{get:function(){return e.memoizedDefaultLocale||(e.memoizedDefaultLocale=new Intl.NumberFormat().resolvedOptions().locale),e.memoizedDefaultLocale;},enumerable:!1,configurable:!0}),e.memoizedDefaultLocale=null,e.resolveLocale=function(e){if(void 0!==Intl.Locale){var t=Intl.NumberFormat.supportedLocalesOf(e);return t.length>0?new Intl.Locale(t[0]):new Intl.Locale("string"==typeof e?e:e[0]);}},e.__parse=vs,e.formats={number:{integer:{maximumFractionDigits:0},currency:{style:"currency"},percent:{style:"percent"}},date:{short:{month:"numeric",day:"numeric",year:"2-digit"},medium:{month:"short",day:"numeric",year:"numeric"},long:{month:"long",day:"numeric",year:"numeric"},full:{weekday:"long",month:"long",day:"numeric",year:"numeric"}},time:{short:{hour:"numeric",minute:"numeric"},medium:{hour:"numeric",minute:"numeric",second:"numeric"},long:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"},full:{hour:"numeric",minute:"numeric",second:"numeric",timeZoneName:"short"}}},e;}(),As=$s;const Ms={de:Jt,en:ga,es:Ta,fr:Va,it:li,nl:Si,no:Bi,sk:an};function Es(e,t,...a){const i=t.replace(/['"]+/g,"");let n;try{n=e.split(".").reduce((e,t)=>e[t],Ms[i]);}catch(t){n=e.split(".").reduce((e,t)=>e[t],Ms.en);}if(void 0===n&&(n=e.split(".").reduce((e,t)=>e[t],Ms.en)),!a.length)return n;const s={};for(let e=0;e<a.length;e+=2){let t=a[e];t=t.replace(/^{([^}]+)?}$/,"$1"),s[t]=a[e+1];}try{return new As(n,t).format(s);}catch(e){return"Translation "+e;}}function Ts(e,t){return(e=e.toString()).split(",")[t];}function Ds(e,t){switch(t){case bt:return e.units==Oe?W`${Nt(st)}`:W`${Nt(rt)}`;case xe:case ht:return e.units==Oe?W`${Nt("mm")}`:W`${Nt("in")}`;case lt:return e.units==Oe?W`${Nt("m<sup>2</sup>")}`:W`${Nt(at)}`;case dt:return e.units==Oe?W`${Nt(it)}`:W`${Nt(nt)}`;default:return W``;}}function js(e,t){!function(e,t){ke(e,"show-dialog",{dialogTag:"error-dialog",dialogImport:()=>Promise.resolve().then(function(){return $r;}),dialogParams:{error:t}});}(t,W`
    ${e.error}:${e.body.message?W` ${e.body.message} `:""}
  `);}const Os=(e,t,a=!1)=>{a?history.replaceState(null,"",t):history.pushState(null,"",t),ke(window,"location-changed",{replace:a});};function Cs(e){var t;if(!e)return"Unknown error";if("string"==typeof e)return e;const a=e;return(null===(t=null==a?void 0:a.body)||void 0===t?void 0:t.message)||(null==a?void 0:a.message)||(null==a?void 0:a.error)||JSON.stringify(e);}function Ps(e,t){e.dispatchEvent(new CustomEvent("hass-notification",{detail:{message:t},bubbles:!0,composed:!0}));}function Ns(e,t,a,i){var n;Ps(e,`${Es(a,null!==(n=null==t?void 0:t.language)&&void 0!==n?n:"en")}: ${Cs(i)}`);}/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */const Hs={},Is=Ot(class extends Ct{constructor(e){if(super(e),e.type!==Dt&&e.type!==Et&&e.type!==jt)throw Error("The `live` directive is not allowed on child or event bindings");if(!(e=>void 0===e.strings)(e))throw Error("`live` bindings can only contain a single expression");}render(e){return e;}update(e,[t]){if(t===F||t===q)return t;const a=e.element,i=e.name;if(e.type===Dt){if(t===a[i])return F;}else if(e.type===jt){if(!!t===a.hasAttribute(i))return F;}else if(e.type===Et&&a.getAttribute(i)===t+"")return F;return((e,t=Hs)=>{e._$AH=t;/**
     * @license
     * Copyright 2020 Google LLC
     * SPDX-License-Identifier: BSD-3-Clause
     */})(e),t;}});var Ls="M19,4H15.5L14.5,3H9.5L8.5,4H5V6H19M6,19A2,2 0 0,0 8,21H16A2,2 0 0,0 18,19V7H6V19Z",Bs="M19,13H13V19H11V13H5V11H11V5H13V11H19V13Z";const Us=e=>e.callWS({type:Se+"/config"}),Rs=e=>e.callWS({type:Se+"/zones"}),Ws=(e,t)=>e.callApi("POST",Se+"/zones",t),Fs=e=>e.callWS({type:Se+"/modules"}),qs=e=>e.callWS({type:Se+"/allmodules"}),Vs=(e,t)=>e.callApi("POST",Se+"/modules",t),Zs=e=>e.callWS({type:Se+"/mappings"}),Ys=(e,t)=>e.callApi("POST",Se+"/mappings",t),Gs=(e,t,a=10)=>e.callWS({type:Se+"/weather_records",mapping_id:t,limit:a}),Ks=e=>e.callWS({type:Se+"/weather_config"}),Xs=(e,t,a)=>e.callWS({type:Se+"/weather_config_test",weather_service:null!=t?t:null,api_key:null!=a?a:null}),Js=(e,t,a,i)=>e.callWS({type:Se+"/weather_config_save",use_weather_service:t,weather_service:null!=a?a:null,api_key:null!=i?i:null}),Qs=e=>{class t extends e{connectedCallback(){super.connectedCallback(),this.__checkSubscribed();}disconnectedCallback(){if(super.disconnectedCallback(),this.__unsubs){for(;this.__unsubs.length;){const e=this.__unsubs.pop();e instanceof Promise?e.then(e=>e()):e();}this.__unsubs=void 0;}}updated(e){super.updated(e),e.has("hass")&&this.__checkSubscribed();}hassSubscribe(){return[];}__checkSubscribed(){void 0===this.__unsubs&&this.isConnected&&void 0!==this.hass&&(this.__unsubs=this.hassSubscribe());}}return n([he({attribute:!1})],t.prototype,"hass",void 0),t;};var er,tr;!function(e){e.Sunrise="sunrise",e.Sunset="sunset",e.SolarAzimuth="solar_azimuth";}(er||(er={})),function(e){e.Disabled="disabled",e.Manual="manual",e.Automatic="automatic";}(tr||(tr={}));const ar=c`
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
`;function ir(e){return e&&e.__esModule&&Object.prototype.hasOwnProperty.call(e,"default")?e.default:e;}function nr(e){throw new Error('Could not dynamically require "'+e+'". Please configure the dynamicRequireTargets or/and ignoreDynamicRequires option of @rollup/plugin-commonjs appropriately for this require call to work.');}c`
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
`;var sr,rr={exports:{}};var or=(sr||(sr=1,function(e){e.exports=function(){var t,a;function i(){return t.apply(null,arguments);}function n(e){t=e;}function s(e){return e instanceof Array||"[object Array]"===Object.prototype.toString.call(e);}function r(e){return null!=e&&"[object Object]"===Object.prototype.toString.call(e);}function o(e,t){return Object.prototype.hasOwnProperty.call(e,t);}function l(e){if(Object.getOwnPropertyNames)return 0===Object.getOwnPropertyNames(e).length;var t;for(t in e)if(o(e,t))return!1;return!0;}function d(e){return void 0===e;}function u(e){return"number"==typeof e||"[object Number]"===Object.prototype.toString.call(e);}function c(e){return e instanceof Date||"[object Date]"===Object.prototype.toString.call(e);}function p(e,t){var a,i=[],n=e.length;for(a=0;a<n;++a)i.push(t(e[a],a));return i;}function h(e,t){for(var a in t)o(t,a)&&(e[a]=t[a]);return o(t,"toString")&&(e.toString=t.toString),o(t,"valueOf")&&(e.valueOf=t.valueOf),e;}function g(e,t,a,i){return Za(e,t,a,i,!0).utc();}function m(){return{empty:!1,unusedTokens:[],unusedInput:[],overflow:-2,charsLeftOver:0,nullInput:!1,invalidEra:null,invalidMonth:null,invalidFormat:!1,userInvalidated:!1,iso:!1,parsedDateParts:[],era:null,meridiem:null,rfc2822:!1,weekdayMismatch:!1};}function v(e){return null==e._pf&&(e._pf=m()),e._pf;}function f(e){var t=null,i=!1,n=e._d&&!isNaN(e._d.getTime());return n&&(t=v(e),i=a.call(t.parsedDateParts,function(e){return null!=e;}),n=t.overflow<0&&!t.empty&&!t.invalidEra&&!t.invalidMonth&&!t.invalidWeekday&&!t.weekdayMismatch&&!t.nullInput&&!t.invalidFormat&&!t.userInvalidated&&(!t.meridiem||t.meridiem&&i),e._strict&&(n=n&&0===t.charsLeftOver&&0===t.unusedTokens.length&&void 0===t.bigHour)),null!=Object.isFrozen&&Object.isFrozen(e)?n:(e._isValid=n,e._isValid);}function _(e){var t=g(NaN);return null!=e?h(v(t),e):v(t).userInvalidated=!0,t;}a=Array.prototype.some?Array.prototype.some:function(e){var t,a=Object(this),i=a.length>>>0;for(t=0;t<i;t++)if(t in a&&e.call(this,a[t],t,a))return!0;return!1;};var b=i.momentProperties=[],y=!1;function w(e,t){var a,i,n,s=b.length;if(d(t._isAMomentObject)||(e._isAMomentObject=t._isAMomentObject),d(t._i)||(e._i=t._i),d(t._f)||(e._f=t._f),d(t._l)||(e._l=t._l),d(t._strict)||(e._strict=t._strict),d(t._tzm)||(e._tzm=t._tzm),d(t._isUTC)||(e._isUTC=t._isUTC),d(t._offset)||(e._offset=t._offset),d(t._pf)||(e._pf=v(t)),d(t._locale)||(e._locale=t._locale),s>0)for(a=0;a<s;a++)d(n=t[i=b[a]])||(e[i]=n);return e;}function k(e){w(this,e),this._d=new Date(null!=e._d?e._d.getTime():NaN),this.isValid()||(this._d=new Date(NaN)),!1===y&&(y=!0,i.updateOffset(this),y=!1);}function z(e){return e instanceof k||null!=e&&null!=e._isAMomentObject;}function S(e){!1===i.suppressDeprecationWarnings&&"undefined"!=typeof console&&console.warn&&console.warn("Deprecation warning: "+e);}function x(e,t){var a=!0;return h(function(){if(null!=i.deprecationHandler&&i.deprecationHandler(null,e),a){var n,s,r,l=[],d=arguments.length;for(s=0;s<d;s++){if(n="","object"==typeof arguments[s]){for(r in n+="\n["+s+"] ",arguments[0])o(arguments[0],r)&&(n+=r+": "+arguments[0][r]+", ");n=n.slice(0,-2);}else n=arguments[s];l.push(n);}S(e+"\nArguments: "+Array.prototype.slice.call(l).join("")+"\n"+new Error().stack),a=!1;}return t.apply(this,arguments);},t);}var $,A={};function M(e,t){null!=i.deprecationHandler&&i.deprecationHandler(e,t),A[e]||(S(t),A[e]=!0);}function E(e){return"undefined"!=typeof Function&&e instanceof Function||"[object Function]"===Object.prototype.toString.call(e);}function T(e){var t,a;for(a in e)o(e,a)&&(E(t=e[a])?this[a]=t:this["_"+a]=t);this._config=e,this._dayOfMonthOrdinalParseLenient=new RegExp((this._dayOfMonthOrdinalParse.source||this._ordinalParse.source)+"|"+/\d{1,2}/.source);}function D(e,t){var a,i=h({},e);for(a in t)o(t,a)&&(r(e[a])&&r(t[a])?(i[a]={},h(i[a],e[a]),h(i[a],t[a])):null!=t[a]?i[a]=t[a]:delete i[a]);for(a in e)o(e,a)&&!o(t,a)&&r(e[a])&&(i[a]=h({},i[a]));return i;}function j(e){null!=e&&this.set(e);}i.suppressDeprecationWarnings=!1,i.deprecationHandler=null,$=Object.keys?Object.keys:function(e){var t,a=[];for(t in e)o(e,t)&&a.push(t);return a;};var O={sameDay:"[Today at] LT",nextDay:"[Tomorrow at] LT",nextWeek:"dddd [at] LT",lastDay:"[Yesterday at] LT",lastWeek:"[Last] dddd [at] LT",sameElse:"L"};function C(e,t,a){var i=this._calendar[e]||this._calendar.sameElse;return E(i)?i.call(t,a):i;}function P(e,t,a){var i=""+Math.abs(e),n=t-i.length;return(e>=0?a?"+":"":"-")+Math.pow(10,Math.max(0,n)).toString().substr(1)+i;}var N=/(\[[^\[]*\])|(\\)?([Hh]mm(ss)?|Mo|MM?M?M?|Do|DDDo|DD?D?D?|ddd?d?|do?|w[o|w]?|W[o|W]?|Qo?|N{1,5}|YYYYYY|YYYYY|YYYY|YY|y{2,4}|yo?|gg(ggg?)?|GG(GGG?)?|e|E|a|A|hh?|HH?|kk?|mm?|ss?|S{1,9}|x|X|zz?|ZZ?|.)/g,H=/(\[[^\[]*\])|(\\)?(LTS|LT|LL?L?L?|l{1,4})/g,I={},L={};function B(e,t,a,i){var n=i;"string"==typeof i&&(n=function(){return this[i]();}),e&&(L[e]=n),t&&(L[t[0]]=function(){return P(n.apply(this,arguments),t[1],t[2]);}),a&&(L[a]=function(){return this.localeData().ordinal(n.apply(this,arguments),e);});}function U(e){return e.match(/\[[\s\S]/)?e.replace(/^\[|\]$/g,""):e.replace(/\\/g,"");}function R(e){var t,a,i=e.match(N);for(t=0,a=i.length;t<a;t++)L[i[t]]?i[t]=L[i[t]]:i[t]=U(i[t]);return function(t){var n,s="";for(n=0;n<a;n++)s+=E(i[n])?i[n].call(t,e):i[n];return s;};}function W(e,t){return e.isValid()?(t=F(t,e.localeData()),I[t]=I[t]||R(t),I[t](e)):e.localeData().invalidDate();}function F(e,t){var a=5;function i(e){return t.longDateFormat(e)||e;}for(H.lastIndex=0;a>=0&&H.test(e);)e=e.replace(H,i),H.lastIndex=0,a-=1;return e;}var q={LTS:"h:mm:ss A",LT:"h:mm A",L:"MM/DD/YYYY",LL:"MMMM D, YYYY",LLL:"MMMM D, YYYY h:mm A",LLLL:"dddd, MMMM D, YYYY h:mm A"};function V(e){var t=this._longDateFormat[e],a=this._longDateFormat[e.toUpperCase()];return t||!a?t:(this._longDateFormat[e]=a.match(N).map(function(e){return"MMMM"===e||"MM"===e||"DD"===e||"dddd"===e?e.slice(1):e;}).join(""),this._longDateFormat[e]);}var Z="Invalid date";function Y(){return this._invalidDate;}var G="%d",K=/\d{1,2}/;function X(e){return this._ordinal.replace("%d",e);}var J={future:"in %s",past:"%s ago",s:"a few seconds",ss:"%d seconds",m:"a minute",mm:"%d minutes",h:"an hour",hh:"%d hours",d:"a day",dd:"%d days",w:"a week",ww:"%d weeks",M:"a month",MM:"%d months",y:"a year",yy:"%d years"};function Q(e,t,a,i){var n=this._relativeTime[a];return E(n)?n(e,t,a,i):n.replace(/%d/i,e);}function ee(e,t){var a=this._relativeTime[e>0?"future":"past"];return E(a)?a(t):a.replace(/%s/i,t);}var te={D:"date",dates:"date",date:"date",d:"day",days:"day",day:"day",e:"weekday",weekdays:"weekday",weekday:"weekday",E:"isoWeekday",isoweekdays:"isoWeekday",isoweekday:"isoWeekday",DDD:"dayOfYear",dayofyears:"dayOfYear",dayofyear:"dayOfYear",h:"hour",hours:"hour",hour:"hour",ms:"millisecond",milliseconds:"millisecond",millisecond:"millisecond",m:"minute",minutes:"minute",minute:"minute",M:"month",months:"month",month:"month",Q:"quarter",quarters:"quarter",quarter:"quarter",s:"second",seconds:"second",second:"second",gg:"weekYear",weekyears:"weekYear",weekyear:"weekYear",GG:"isoWeekYear",isoweekyears:"isoWeekYear",isoweekyear:"isoWeekYear",w:"week",weeks:"week",week:"week",W:"isoWeek",isoweeks:"isoWeek",isoweek:"isoWeek",y:"year",years:"year",year:"year"};function ae(e){return"string"==typeof e?te[e]||te[e.toLowerCase()]:void 0;}function ie(e){var t,a,i={};for(a in e)o(e,a)&&(t=ae(a))&&(i[t]=e[a]);return i;}var ne={date:9,day:11,weekday:11,isoWeekday:11,dayOfYear:4,hour:13,millisecond:16,minute:14,month:8,quarter:7,second:15,weekYear:1,isoWeekYear:1,week:5,isoWeek:5,year:1};function se(e){var t,a=[];for(t in e)o(e,t)&&a.push({unit:t,priority:ne[t]});return a.sort(function(e,t){return e.priority-t.priority;}),a;}var re,oe=/\d/,le=/\d\d/,de=/\d{3}/,ue=/\d{4}/,ce=/[+-]?\d{6}/,pe=/\d\d?/,he=/\d\d\d\d?/,ge=/\d\d\d\d\d\d?/,me=/\d{1,3}/,ve=/\d{1,4}/,fe=/[+-]?\d{1,6}/,_e=/\d+/,be=/[+-]?\d+/,ye=/Z|[+-]\d\d:?\d\d/gi,we=/Z|[+-]\d\d(?::?\d\d)?/gi,ke=/[+-]?\d+(\.\d{1,3})?/,ze=/[0-9]{0,256}['a-z\u00A0-\u05FF\u0700-\uD7FF\uF900-\uFDCF\uFDF0-\uFF07\uFF10-\uFFEF]{1,256}|[\u0600-\u06FF\/]{1,256}(\s*?[\u0600-\u06FF]{1,256}){1,2}/i,Se=/^[1-9]\d?/,xe=/^([1-9]\d|\d)/;function $e(e,t,a){re[e]=E(t)?t:function(e,i){return e&&a?a:t;};}function Ae(e,t){return o(re,e)?re[e](t._strict,t._locale):new RegExp(Me(e));}function Me(e){return Ee(e.replace("\\","").replace(/\\(\[)|\\(\])|\[([^\]\[]*)\]|\\(.)/g,function(e,t,a,i,n){return t||a||i||n;}));}function Ee(e){return e.replace(/[-\/\\^$*+?.()|[\]{}]/g,"\\$&");}function Te(e){return e<0?Math.ceil(e)||0:Math.floor(e);}function De(e){var t=+e,a=0;return 0!==t&&isFinite(t)&&(a=Te(t)),a;}re={};var je={};function Oe(e,t){var a,i,n=t;for("string"==typeof e&&(e=[e]),u(t)&&(n=function(e,a){a[t]=De(e);}),i=e.length,a=0;a<i;a++)je[e[a]]=n;}function Ce(e,t){Oe(e,function(e,a,i,n){i._w=i._w||{},t(e,i._w,i,n);});}function Pe(e,t,a){null!=t&&o(je,e)&&je[e](t,a._a,a,e);}function Ne(e){return e%4==0&&e%100!=0||e%400==0;}var He=0,Ie=1,Le=2,Be=3,Ue=4,Re=5,We=6,Fe=7,qe=8;function Ve(e){return Ne(e)?366:365;}B("Y",0,0,function(){var e=this.year();return e<=9999?P(e,4):"+"+e;}),B(0,["YY",2],0,function(){return this.year()%100;}),B(0,["YYYY",4],0,"year"),B(0,["YYYYY",5],0,"year"),B(0,["YYYYYY",6,!0],0,"year"),$e("Y",be),$e("YY",pe,le),$e("YYYY",ve,ue),$e("YYYYY",fe,ce),$e("YYYYYY",fe,ce),Oe(["YYYYY","YYYYYY"],He),Oe("YYYY",function(e,t){t[He]=2===e.length?i.parseTwoDigitYear(e):De(e);}),Oe("YY",function(e,t){t[He]=i.parseTwoDigitYear(e);}),Oe("Y",function(e,t){t[He]=parseInt(e,10);}),i.parseTwoDigitYear=function(e){return De(e)+(De(e)>68?1900:2e3);};var Ze,Ye=Ke("FullYear",!0);function Ge(){return Ne(this.year());}function Ke(e,t){return function(a){return null!=a?(Je(this,e,a),i.updateOffset(this,t),this):Xe(this,e);};}function Xe(e,t){if(!e.isValid())return NaN;var a=e._d,i=e._isUTC;switch(t){case"Milliseconds":return i?a.getUTCMilliseconds():a.getMilliseconds();case"Seconds":return i?a.getUTCSeconds():a.getSeconds();case"Minutes":return i?a.getUTCMinutes():a.getMinutes();case"Hours":return i?a.getUTCHours():a.getHours();case"Date":return i?a.getUTCDate():a.getDate();case"Day":return i?a.getUTCDay():a.getDay();case"Month":return i?a.getUTCMonth():a.getMonth();case"FullYear":return i?a.getUTCFullYear():a.getFullYear();default:return NaN;}}function Je(e,t,a){var i,n,s,r,o;if(e.isValid()&&!isNaN(a)){switch(i=e._d,n=e._isUTC,t){case"Milliseconds":return void(n?i.setUTCMilliseconds(a):i.setMilliseconds(a));case"Seconds":return void(n?i.setUTCSeconds(a):i.setSeconds(a));case"Minutes":return void(n?i.setUTCMinutes(a):i.setMinutes(a));case"Hours":return void(n?i.setUTCHours(a):i.setHours(a));case"Date":return void(n?i.setUTCDate(a):i.setDate(a));case"FullYear":break;default:return;}s=a,r=e.month(),o=29!==(o=e.date())||1!==r||Ne(s)?o:28,n?i.setUTCFullYear(s,r,o):i.setFullYear(s,r,o);}}function Qe(e){return E(this[e=ae(e)])?this[e]():this;}function et(e,t){if("object"==typeof e){var a,i=se(e=ie(e)),n=i.length;for(a=0;a<n;a++)this[i[a].unit](e[i[a].unit]);}else if(E(this[e=ae(e)]))return this[e](t);return this;}function tt(e,t){return(e%t+t)%t;}function at(e,t){if(isNaN(e)||isNaN(t))return NaN;var a=tt(t,12);return e+=(t-a)/12,1===a?Ne(e)?29:28:31-a%7%2;}Ze=Array.prototype.indexOf?Array.prototype.indexOf:function(e){var t;for(t=0;t<this.length;++t)if(this[t]===e)return t;return-1;},B("M",["MM",2],"Mo",function(){return this.month()+1;}),B("MMM",0,0,function(e){return this.localeData().monthsShort(this,e);}),B("MMMM",0,0,function(e){return this.localeData().months(this,e);}),$e("M",pe,Se),$e("MM",pe,le),$e("MMM",function(e,t){return t.monthsShortRegex(e);}),$e("MMMM",function(e,t){return t.monthsRegex(e);}),Oe(["M","MM"],function(e,t){t[Ie]=De(e)-1;}),Oe(["MMM","MMMM"],function(e,t,a,i){var n=a._locale.monthsParse(e,i,a._strict);null!=n?t[Ie]=n:v(a).invalidMonth=e;});var it="January_February_March_April_May_June_July_August_September_October_November_December".split("_"),nt="Jan_Feb_Mar_Apr_May_Jun_Jul_Aug_Sep_Oct_Nov_Dec".split("_"),st=/D[oD]?(\[[^\[\]]*\]|\s)+MMMM?/,rt=ze,ot=ze;function lt(e,t){return e?s(this._months)?this._months[e.month()]:this._months[(this._months.isFormat||st).test(t)?"format":"standalone"][e.month()]:s(this._months)?this._months:this._months.standalone;}function dt(e,t){return e?s(this._monthsShort)?this._monthsShort[e.month()]:this._monthsShort[st.test(t)?"format":"standalone"][e.month()]:s(this._monthsShort)?this._monthsShort:this._monthsShort.standalone;}function ut(e,t,a){var i,n,s,r=e.toLocaleLowerCase();if(!this._monthsParse)for(this._monthsParse=[],this._longMonthsParse=[],this._shortMonthsParse=[],i=0;i<12;++i)s=g([2e3,i]),this._shortMonthsParse[i]=this.monthsShort(s,"").toLocaleLowerCase(),this._longMonthsParse[i]=this.months(s,"").toLocaleLowerCase();return a?"MMM"===t?-1!==(n=Ze.call(this._shortMonthsParse,r))?n:null:-1!==(n=Ze.call(this._longMonthsParse,r))?n:null:"MMM"===t?-1!==(n=Ze.call(this._shortMonthsParse,r))||-1!==(n=Ze.call(this._longMonthsParse,r))?n:null:-1!==(n=Ze.call(this._longMonthsParse,r))||-1!==(n=Ze.call(this._shortMonthsParse,r))?n:null;}function ct(e,t,a){var i,n,s;if(this._monthsParseExact)return ut.call(this,e,t,a);for(this._monthsParse||(this._monthsParse=[],this._longMonthsParse=[],this._shortMonthsParse=[]),i=0;i<12;i++){if(n=g([2e3,i]),a&&!this._longMonthsParse[i]&&(this._longMonthsParse[i]=new RegExp("^"+this.months(n,"").replace(".","")+"$","i"),this._shortMonthsParse[i]=new RegExp("^"+this.monthsShort(n,"").replace(".","")+"$","i")),a||this._monthsParse[i]||(s="^"+this.months(n,"")+"|^"+this.monthsShort(n,""),this._monthsParse[i]=new RegExp(s.replace(".",""),"i")),a&&"MMMM"===t&&this._longMonthsParse[i].test(e))return i;if(a&&"MMM"===t&&this._shortMonthsParse[i].test(e))return i;if(!a&&this._monthsParse[i].test(e))return i;}}function pt(e,t){if(!e.isValid())return e;if("string"==typeof t)if(/^\d+$/.test(t))t=De(t);else if(!u(t=e.localeData().monthsParse(t)))return e;var a=t,i=e.date();return i=i<29?i:Math.min(i,at(e.year(),a)),e._isUTC?e._d.setUTCMonth(a,i):e._d.setMonth(a,i),e;}function ht(e){return null!=e?(pt(this,e),i.updateOffset(this,!0),this):Xe(this,"Month");}function gt(){return at(this.year(),this.month());}function mt(e){return this._monthsParseExact?(o(this,"_monthsRegex")||ft.call(this),e?this._monthsShortStrictRegex:this._monthsShortRegex):(o(this,"_monthsShortRegex")||(this._monthsShortRegex=rt),this._monthsShortStrictRegex&&e?this._monthsShortStrictRegex:this._monthsShortRegex);}function vt(e){return this._monthsParseExact?(o(this,"_monthsRegex")||ft.call(this),e?this._monthsStrictRegex:this._monthsRegex):(o(this,"_monthsRegex")||(this._monthsRegex=ot),this._monthsStrictRegex&&e?this._monthsStrictRegex:this._monthsRegex);}function ft(){function e(e,t){return t.length-e.length;}var t,a,i,n,s=[],r=[],o=[];for(t=0;t<12;t++)a=g([2e3,t]),i=Ee(this.monthsShort(a,"")),n=Ee(this.months(a,"")),s.push(i),r.push(n),o.push(n),o.push(i);s.sort(e),r.sort(e),o.sort(e),this._monthsRegex=new RegExp("^("+o.join("|")+")","i"),this._monthsShortRegex=this._monthsRegex,this._monthsStrictRegex=new RegExp("^("+r.join("|")+")","i"),this._monthsShortStrictRegex=new RegExp("^("+s.join("|")+")","i");}function _t(e,t,a,i,n,s,r){var o;return e<100&&e>=0?(o=new Date(e+400,t,a,i,n,s,r),isFinite(o.getFullYear())&&o.setFullYear(e)):o=new Date(e,t,a,i,n,s,r),o;}function bt(e){var t,a;return e<100&&e>=0?((a=Array.prototype.slice.call(arguments))[0]=e+400,t=new Date(Date.UTC.apply(null,a)),isFinite(t.getUTCFullYear())&&t.setUTCFullYear(e)):t=new Date(Date.UTC.apply(null,arguments)),t;}function yt(e,t,a){var i=7+t-a;return-(7+bt(e,0,i).getUTCDay()-t)%7+i-1;}function wt(e,t,a,i,n){var s,r,o=1+7*(t-1)+(7+a-i)%7+yt(e,i,n);return o<=0?r=Ve(s=e-1)+o:o>Ve(e)?(s=e+1,r=o-Ve(e)):(s=e,r=o),{year:s,dayOfYear:r};}function kt(e,t,a){var i,n,s=yt(e.year(),t,a),r=Math.floor((e.dayOfYear()-s-1)/7)+1;return r<1?i=r+zt(n=e.year()-1,t,a):r>zt(e.year(),t,a)?(i=r-zt(e.year(),t,a),n=e.year()+1):(n=e.year(),i=r),{week:i,year:n};}function zt(e,t,a){var i=yt(e,t,a),n=yt(e+1,t,a);return(Ve(e)-i+n)/7;}function St(e){return kt(e,this._week.dow,this._week.doy).week;}B("w",["ww",2],"wo","week"),B("W",["WW",2],"Wo","isoWeek"),$e("w",pe,Se),$e("ww",pe,le),$e("W",pe,Se),$e("WW",pe,le),Ce(["w","ww","W","WW"],function(e,t,a,i){t[i.substr(0,1)]=De(e);});var xt={dow:0,doy:6};function $t(){return this._week.dow;}function At(){return this._week.doy;}function Mt(e){var t=this.localeData().week(this);return null==e?t:this.add(7*(e-t),"d");}function Et(e){var t=kt(this,1,4).week;return null==e?t:this.add(7*(e-t),"d");}function Tt(e,t){return"string"!=typeof e?e:isNaN(e)?"number"==typeof(e=t.weekdaysParse(e))?e:null:parseInt(e,10);}function Dt(e,t){return"string"==typeof e?t.weekdaysParse(e)%7||7:isNaN(e)?null:e;}function jt(e,t){return e.slice(t,7).concat(e.slice(0,t));}B("d",0,"do","day"),B("dd",0,0,function(e){return this.localeData().weekdaysMin(this,e);}),B("ddd",0,0,function(e){return this.localeData().weekdaysShort(this,e);}),B("dddd",0,0,function(e){return this.localeData().weekdays(this,e);}),B("e",0,0,"weekday"),B("E",0,0,"isoWeekday"),$e("d",pe),$e("e",pe),$e("E",pe),$e("dd",function(e,t){return t.weekdaysMinRegex(e);}),$e("ddd",function(e,t){return t.weekdaysShortRegex(e);}),$e("dddd",function(e,t){return t.weekdaysRegex(e);}),Ce(["dd","ddd","dddd"],function(e,t,a,i){var n=a._locale.weekdaysParse(e,i,a._strict);null!=n?t.d=n:v(a).invalidWeekday=e;}),Ce(["d","e","E"],function(e,t,a,i){t[i]=De(e);});var Ot="Sunday_Monday_Tuesday_Wednesday_Thursday_Friday_Saturday".split("_"),Ct="Sun_Mon_Tue_Wed_Thu_Fri_Sat".split("_"),Pt="Su_Mo_Tu_We_Th_Fr_Sa".split("_"),Nt=ze,Ht=ze,It=ze;function Lt(e,t){var a=s(this._weekdays)?this._weekdays:this._weekdays[e&&!0!==e&&this._weekdays.isFormat.test(t)?"format":"standalone"];return!0===e?jt(a,this._week.dow):e?a[e.day()]:a;}function Bt(e){return!0===e?jt(this._weekdaysShort,this._week.dow):e?this._weekdaysShort[e.day()]:this._weekdaysShort;}function Ut(e){return!0===e?jt(this._weekdaysMin,this._week.dow):e?this._weekdaysMin[e.day()]:this._weekdaysMin;}function Rt(e,t,a){var i,n,s,r=e.toLocaleLowerCase();if(!this._weekdaysParse)for(this._weekdaysParse=[],this._shortWeekdaysParse=[],this._minWeekdaysParse=[],i=0;i<7;++i)s=g([2e3,1]).day(i),this._minWeekdaysParse[i]=this.weekdaysMin(s,"").toLocaleLowerCase(),this._shortWeekdaysParse[i]=this.weekdaysShort(s,"").toLocaleLowerCase(),this._weekdaysParse[i]=this.weekdays(s,"").toLocaleLowerCase();return a?"dddd"===t?-1!==(n=Ze.call(this._weekdaysParse,r))?n:null:"ddd"===t?-1!==(n=Ze.call(this._shortWeekdaysParse,r))?n:null:-1!==(n=Ze.call(this._minWeekdaysParse,r))?n:null:"dddd"===t?-1!==(n=Ze.call(this._weekdaysParse,r))||-1!==(n=Ze.call(this._shortWeekdaysParse,r))||-1!==(n=Ze.call(this._minWeekdaysParse,r))?n:null:"ddd"===t?-1!==(n=Ze.call(this._shortWeekdaysParse,r))||-1!==(n=Ze.call(this._weekdaysParse,r))||-1!==(n=Ze.call(this._minWeekdaysParse,r))?n:null:-1!==(n=Ze.call(this._minWeekdaysParse,r))||-1!==(n=Ze.call(this._weekdaysParse,r))||-1!==(n=Ze.call(this._shortWeekdaysParse,r))?n:null;}function Wt(e,t,a){var i,n,s;if(this._weekdaysParseExact)return Rt.call(this,e,t,a);for(this._weekdaysParse||(this._weekdaysParse=[],this._minWeekdaysParse=[],this._shortWeekdaysParse=[],this._fullWeekdaysParse=[]),i=0;i<7;i++){if(n=g([2e3,1]).day(i),a&&!this._fullWeekdaysParse[i]&&(this._fullWeekdaysParse[i]=new RegExp("^"+this.weekdays(n,"").replace(".","\\.?")+"$","i"),this._shortWeekdaysParse[i]=new RegExp("^"+this.weekdaysShort(n,"").replace(".","\\.?")+"$","i"),this._minWeekdaysParse[i]=new RegExp("^"+this.weekdaysMin(n,"").replace(".","\\.?")+"$","i")),this._weekdaysParse[i]||(s="^"+this.weekdays(n,"")+"|^"+this.weekdaysShort(n,"")+"|^"+this.weekdaysMin(n,""),this._weekdaysParse[i]=new RegExp(s.replace(".",""),"i")),a&&"dddd"===t&&this._fullWeekdaysParse[i].test(e))return i;if(a&&"ddd"===t&&this._shortWeekdaysParse[i].test(e))return i;if(a&&"dd"===t&&this._minWeekdaysParse[i].test(e))return i;if(!a&&this._weekdaysParse[i].test(e))return i;}}function Ft(e){if(!this.isValid())return null!=e?this:NaN;var t=Xe(this,"Day");return null!=e?(e=Tt(e,this.localeData()),this.add(e-t,"d")):t;}function qt(e){if(!this.isValid())return null!=e?this:NaN;var t=(this.day()+7-this.localeData()._week.dow)%7;return null==e?t:this.add(e-t,"d");}function Vt(e){if(!this.isValid())return null!=e?this:NaN;if(null!=e){var t=Dt(e,this.localeData());return this.day(this.day()%7?t:t-7);}return this.day()||7;}function Zt(e){return this._weekdaysParseExact?(o(this,"_weekdaysRegex")||Kt.call(this),e?this._weekdaysStrictRegex:this._weekdaysRegex):(o(this,"_weekdaysRegex")||(this._weekdaysRegex=Nt),this._weekdaysStrictRegex&&e?this._weekdaysStrictRegex:this._weekdaysRegex);}function Yt(e){return this._weekdaysParseExact?(o(this,"_weekdaysRegex")||Kt.call(this),e?this._weekdaysShortStrictRegex:this._weekdaysShortRegex):(o(this,"_weekdaysShortRegex")||(this._weekdaysShortRegex=Ht),this._weekdaysShortStrictRegex&&e?this._weekdaysShortStrictRegex:this._weekdaysShortRegex);}function Gt(e){return this._weekdaysParseExact?(o(this,"_weekdaysRegex")||Kt.call(this),e?this._weekdaysMinStrictRegex:this._weekdaysMinRegex):(o(this,"_weekdaysMinRegex")||(this._weekdaysMinRegex=It),this._weekdaysMinStrictRegex&&e?this._weekdaysMinStrictRegex:this._weekdaysMinRegex);}function Kt(){function e(e,t){return t.length-e.length;}var t,a,i,n,s,r=[],o=[],l=[],d=[];for(t=0;t<7;t++)a=g([2e3,1]).day(t),i=Ee(this.weekdaysMin(a,"")),n=Ee(this.weekdaysShort(a,"")),s=Ee(this.weekdays(a,"")),r.push(i),o.push(n),l.push(s),d.push(i),d.push(n),d.push(s);r.sort(e),o.sort(e),l.sort(e),d.sort(e),this._weekdaysRegex=new RegExp("^("+d.join("|")+")","i"),this._weekdaysShortRegex=this._weekdaysRegex,this._weekdaysMinRegex=this._weekdaysRegex,this._weekdaysStrictRegex=new RegExp("^("+l.join("|")+")","i"),this._weekdaysShortStrictRegex=new RegExp("^("+o.join("|")+")","i"),this._weekdaysMinStrictRegex=new RegExp("^("+r.join("|")+")","i");}function Xt(){return this.hours()%12||12;}function Jt(){return this.hours()||24;}function Qt(e,t){B(e,0,0,function(){return this.localeData().meridiem(this.hours(),this.minutes(),t);});}function ea(e,t){return t._meridiemParse;}function ta(e){return"p"===(e+"").toLowerCase().charAt(0);}B("H",["HH",2],0,"hour"),B("h",["hh",2],0,Xt),B("k",["kk",2],0,Jt),B("hmm",0,0,function(){return""+Xt.apply(this)+P(this.minutes(),2);}),B("hmmss",0,0,function(){return""+Xt.apply(this)+P(this.minutes(),2)+P(this.seconds(),2);}),B("Hmm",0,0,function(){return""+this.hours()+P(this.minutes(),2);}),B("Hmmss",0,0,function(){return""+this.hours()+P(this.minutes(),2)+P(this.seconds(),2);}),Qt("a",!0),Qt("A",!1),$e("a",ea),$e("A",ea),$e("H",pe,xe),$e("h",pe,Se),$e("k",pe,Se),$e("HH",pe,le),$e("hh",pe,le),$e("kk",pe,le),$e("hmm",he),$e("hmmss",ge),$e("Hmm",he),$e("Hmmss",ge),Oe(["H","HH"],Be),Oe(["k","kk"],function(e,t,a){var i=De(e);t[Be]=24===i?0:i;}),Oe(["a","A"],function(e,t,a){a._isPm=a._locale.isPM(e),a._meridiem=e;}),Oe(["h","hh"],function(e,t,a){t[Be]=De(e),v(a).bigHour=!0;}),Oe("hmm",function(e,t,a){var i=e.length-2;t[Be]=De(e.substr(0,i)),t[Ue]=De(e.substr(i)),v(a).bigHour=!0;}),Oe("hmmss",function(e,t,a){var i=e.length-4,n=e.length-2;t[Be]=De(e.substr(0,i)),t[Ue]=De(e.substr(i,2)),t[Re]=De(e.substr(n)),v(a).bigHour=!0;}),Oe("Hmm",function(e,t,a){var i=e.length-2;t[Be]=De(e.substr(0,i)),t[Ue]=De(e.substr(i));}),Oe("Hmmss",function(e,t,a){var i=e.length-4,n=e.length-2;t[Be]=De(e.substr(0,i)),t[Ue]=De(e.substr(i,2)),t[Re]=De(e.substr(n));});var aa=/[ap]\.?m?\.?/i,ia=Ke("Hours",!0);function na(e,t,a){return e>11?a?"pm":"PM":a?"am":"AM";}var sa,ra={calendar:O,longDateFormat:q,invalidDate:Z,ordinal:G,dayOfMonthOrdinalParse:K,relativeTime:J,months:it,monthsShort:nt,week:xt,weekdays:Ot,weekdaysMin:Pt,weekdaysShort:Ct,meridiemParse:aa},oa={},la={};function da(e,t){var a,i=Math.min(e.length,t.length);for(a=0;a<i;a+=1)if(e[a]!==t[a])return a;return i;}function ua(e){return e?e.toLowerCase().replace("_","-"):e;}function ca(e){for(var t,a,i,n,s=0;s<e.length;){for(t=(n=ua(e[s]).split("-")).length,a=(a=ua(e[s+1]))?a.split("-"):null;t>0;){if(i=ha(n.slice(0,t).join("-")))return i;if(a&&a.length>=t&&da(n,a)>=t-1)break;t--;}s++;}return sa;}function pa(e){return!(!e||!e.match("^[^/\\\\]*$"));}function ha(t){var a=null;if(void 0===oa[t]&&e&&e.exports&&pa(t))try{a=sa._abbr,nr("./locale/"+t),ga(a);}catch(e){oa[t]=null;}return oa[t];}function ga(e,t){var a;return e&&((a=d(t)?fa(e):ma(e,t))?sa=a:"undefined"!=typeof console&&console.warn&&console.warn("Locale "+e+" not found. Did you forget to load it?")),sa._abbr;}function ma(e,t){if(null!==t){var a,i=ra;if(t.abbr=e,null!=oa[e])M("defineLocaleOverride","use moment.updateLocale(localeName, config) to change an existing locale. moment.defineLocale(localeName, config) should only be used for creating a new locale See http://momentjs.com/guides/#/warnings/define-locale/ for more info."),i=oa[e]._config;else if(null!=t.parentLocale)if(null!=oa[t.parentLocale])i=oa[t.parentLocale]._config;else{if(null==(a=ha(t.parentLocale)))return la[t.parentLocale]||(la[t.parentLocale]=[]),la[t.parentLocale].push({name:e,config:t}),null;i=a._config;}return oa[e]=new j(D(i,t)),la[e]&&la[e].forEach(function(e){ma(e.name,e.config);}),ga(e),oa[e];}return delete oa[e],null;}function va(e,t){if(null!=t){var a,i,n=ra;null!=oa[e]&&null!=oa[e].parentLocale?oa[e].set(D(oa[e]._config,t)):(null!=(i=ha(e))&&(n=i._config),t=D(n,t),null==i&&(t.abbr=e),(a=new j(t)).parentLocale=oa[e],oa[e]=a),ga(e);}else null!=oa[e]&&(null!=oa[e].parentLocale?(oa[e]=oa[e].parentLocale,e===ga()&&ga(e)):null!=oa[e]&&delete oa[e]);return oa[e];}function fa(e){var t;if(e&&e._locale&&e._locale._abbr&&(e=e._locale._abbr),!e)return sa;if(!s(e)){if(t=ha(e))return t;e=[e];}return ca(e);}function _a(){return $(oa);}function ba(e){var t,a=e._a;return a&&-2===v(e).overflow&&(t=a[Ie]<0||a[Ie]>11?Ie:a[Le]<1||a[Le]>at(a[He],a[Ie])?Le:a[Be]<0||a[Be]>24||24===a[Be]&&(0!==a[Ue]||0!==a[Re]||0!==a[We])?Be:a[Ue]<0||a[Ue]>59?Ue:a[Re]<0||a[Re]>59?Re:a[We]<0||a[We]>999?We:-1,v(e)._overflowDayOfYear&&(t<He||t>Le)&&(t=Le),v(e)._overflowWeeks&&-1===t&&(t=Fe),v(e)._overflowWeekday&&-1===t&&(t=qe),v(e).overflow=t),e;}var ya=/^\s*((?:[+-]\d{6}|\d{4})-(?:\d\d-\d\d|W\d\d-\d|W\d\d|\d\d\d|\d\d))(?:(T| )(\d\d(?::\d\d(?::\d\d(?:[.,]\d+)?)?)?)([+-]\d\d(?::?\d\d)?|\s*Z)?)?$/,wa=/^\s*((?:[+-]\d{6}|\d{4})(?:\d\d\d\d|W\d\d\d|W\d\d|\d\d\d|\d\d|))(?:(T| )(\d\d(?:\d\d(?:\d\d(?:[.,]\d+)?)?)?)([+-]\d\d(?::?\d\d)?|\s*Z)?)?$/,ka=/Z|[+-]\d\d(?::?\d\d)?/,za=[["YYYYYY-MM-DD",/[+-]\d{6}-\d\d-\d\d/],["YYYY-MM-DD",/\d{4}-\d\d-\d\d/],["GGGG-[W]WW-E",/\d{4}-W\d\d-\d/],["GGGG-[W]WW",/\d{4}-W\d\d/,!1],["YYYY-DDD",/\d{4}-\d{3}/],["YYYY-MM",/\d{4}-\d\d/,!1],["YYYYYYMMDD",/[+-]\d{10}/],["YYYYMMDD",/\d{8}/],["GGGG[W]WWE",/\d{4}W\d{3}/],["GGGG[W]WW",/\d{4}W\d{2}/,!1],["YYYYDDD",/\d{7}/],["YYYYMM",/\d{6}/,!1],["YYYY",/\d{4}/,!1]],Sa=[["HH:mm:ss.SSSS",/\d\d:\d\d:\d\d\.\d+/],["HH:mm:ss,SSSS",/\d\d:\d\d:\d\d,\d+/],["HH:mm:ss",/\d\d:\d\d:\d\d/],["HH:mm",/\d\d:\d\d/],["HHmmss.SSSS",/\d\d\d\d\d\d\.\d+/],["HHmmss,SSSS",/\d\d\d\d\d\d,\d+/],["HHmmss",/\d\d\d\d\d\d/],["HHmm",/\d\d\d\d/],["HH",/\d\d/]],xa=/^\/?Date\((-?\d+)/i,$a=/^(?:(Mon|Tue|Wed|Thu|Fri|Sat|Sun),?\s)?(\d{1,2})\s(Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s(\d{2,4})\s(\d\d):(\d\d)(?::(\d\d))?\s(?:(UT|GMT|[ECMP][SD]T)|([Zz])|([+-]\d{4}))$/,Aa={UT:0,GMT:0,EDT:-240,EST:-300,CDT:-300,CST:-360,MDT:-360,MST:-420,PDT:-420,PST:-480};function Ma(e){var t,a,i,n,s,r,o=e._i,l=ya.exec(o)||wa.exec(o),d=za.length,u=Sa.length;if(l){for(v(e).iso=!0,t=0,a=d;t<a;t++)if(za[t][1].exec(l[1])){n=za[t][0],i=!1!==za[t][2];break;}if(null==n)return void(e._isValid=!1);if(l[3]){for(t=0,a=u;t<a;t++)if(Sa[t][1].exec(l[3])){s=(l[2]||" ")+Sa[t][0];break;}if(null==s)return void(e._isValid=!1);}if(!i&&null!=s)return void(e._isValid=!1);if(l[4]){if(!ka.exec(l[4]))return void(e._isValid=!1);r="Z";}e._f=n+(s||"")+(r||""),Ba(e);}else e._isValid=!1;}function Ea(e,t,a,i,n,s){var r=[Ta(e),nt.indexOf(t),parseInt(a,10),parseInt(i,10),parseInt(n,10)];return s&&r.push(parseInt(s,10)),r;}function Ta(e){var t=parseInt(e,10);return t<=49?2e3+t:t<=999?1900+t:t;}function Da(e){return e.replace(/\([^()]*\)|[\n\t]/g," ").replace(/(\s\s+)/g," ").replace(/^\s\s*/,"").replace(/\s\s*$/,"");}function ja(e,t,a){return!e||Ct.indexOf(e)===new Date(t[0],t[1],t[2]).getDay()||(v(a).weekdayMismatch=!0,a._isValid=!1,!1);}function Oa(e,t,a){if(e)return Aa[e];if(t)return 0;var i=parseInt(a,10),n=i%100;return(i-n)/100*60+n;}function Ca(e){var t,a=$a.exec(Da(e._i));if(a){if(t=Ea(a[4],a[3],a[2],a[5],a[6],a[7]),!ja(a[1],t,e))return;e._a=t,e._tzm=Oa(a[8],a[9],a[10]),e._d=bt.apply(null,e._a),e._d.setUTCMinutes(e._d.getUTCMinutes()-e._tzm),v(e).rfc2822=!0;}else e._isValid=!1;}function Pa(e){var t=xa.exec(e._i);null===t?(Ma(e),!1===e._isValid&&(delete e._isValid,Ca(e),!1===e._isValid&&(delete e._isValid,e._strict?e._isValid=!1:i.createFromInputFallback(e)))):e._d=new Date(+t[1]);}function Na(e,t,a){return null!=e?e:null!=t?t:a;}function Ha(e){var t=new Date(i.now());return e._useUTC?[t.getUTCFullYear(),t.getUTCMonth(),t.getUTCDate()]:[t.getFullYear(),t.getMonth(),t.getDate()];}function Ia(e){var t,a,i,n,s,r=[];if(!e._d){for(i=Ha(e),e._w&&null==e._a[Le]&&null==e._a[Ie]&&La(e),null!=e._dayOfYear&&(s=Na(e._a[He],i[He]),(e._dayOfYear>Ve(s)||0===e._dayOfYear)&&(v(e)._overflowDayOfYear=!0),a=bt(s,0,e._dayOfYear),e._a[Ie]=a.getUTCMonth(),e._a[Le]=a.getUTCDate()),t=0;t<3&&null==e._a[t];++t)e._a[t]=r[t]=i[t];for(;t<7;t++)e._a[t]=r[t]=null==e._a[t]?2===t?1:0:e._a[t];24===e._a[Be]&&0===e._a[Ue]&&0===e._a[Re]&&0===e._a[We]&&(e._nextDay=!0,e._a[Be]=0),e._d=(e._useUTC?bt:_t).apply(null,r),n=e._useUTC?e._d.getUTCDay():e._d.getDay(),null!=e._tzm&&e._d.setUTCMinutes(e._d.getUTCMinutes()-e._tzm),e._nextDay&&(e._a[Be]=24),e._w&&void 0!==e._w.d&&e._w.d!==n&&(v(e).weekdayMismatch=!0);}}function La(e){var t,a,i,n,s,r,o,l,d;null!=(t=e._w).GG||null!=t.W||null!=t.E?(s=1,r=4,a=Na(t.GG,e._a[He],kt(Ya(),1,4).year),i=Na(t.W,1),((n=Na(t.E,1))<1||n>7)&&(l=!0)):(s=e._locale._week.dow,r=e._locale._week.doy,d=kt(Ya(),s,r),a=Na(t.gg,e._a[He],d.year),i=Na(t.w,d.week),null!=t.d?((n=t.d)<0||n>6)&&(l=!0):null!=t.e?(n=t.e+s,(t.e<0||t.e>6)&&(l=!0)):n=s),i<1||i>zt(a,s,r)?v(e)._overflowWeeks=!0:null!=l?v(e)._overflowWeekday=!0:(o=wt(a,i,n,s,r),e._a[He]=o.year,e._dayOfYear=o.dayOfYear);}function Ba(e){if(e._f!==i.ISO_8601){if(e._f!==i.RFC_2822){e._a=[],v(e).empty=!0;var t,a,n,s,r,o,l,d=""+e._i,u=d.length,c=0;for(l=(n=F(e._f,e._locale).match(N)||[]).length,t=0;t<l;t++)s=n[t],(a=(d.match(Ae(s,e))||[])[0])&&((r=d.substr(0,d.indexOf(a))).length>0&&v(e).unusedInput.push(r),d=d.slice(d.indexOf(a)+a.length),c+=a.length),L[s]?(a?v(e).empty=!1:v(e).unusedTokens.push(s),Pe(s,a,e)):e._strict&&!a&&v(e).unusedTokens.push(s);v(e).charsLeftOver=u-c,d.length>0&&v(e).unusedInput.push(d),e._a[Be]<=12&&!0===v(e).bigHour&&e._a[Be]>0&&(v(e).bigHour=void 0),v(e).parsedDateParts=e._a.slice(0),v(e).meridiem=e._meridiem,e._a[Be]=Ua(e._locale,e._a[Be],e._meridiem),null!==(o=v(e).era)&&(e._a[He]=e._locale.erasConvertYear(o,e._a[He])),Ia(e),ba(e);}else Ca(e);}else Ma(e);}function Ua(e,t,a){var i;return null==a?t:null!=e.meridiemHour?e.meridiemHour(t,a):null!=e.isPM?((i=e.isPM(a))&&t<12&&(t+=12),i||12!==t||(t=0),t):t;}function Ra(e){var t,a,i,n,s,r,o=!1,l=e._f.length;if(0===l)return v(e).invalidFormat=!0,void(e._d=new Date(NaN));for(n=0;n<l;n++)s=0,r=!1,t=w({},e),null!=e._useUTC&&(t._useUTC=e._useUTC),t._f=e._f[n],Ba(t),f(t)&&(r=!0),s+=v(t).charsLeftOver,s+=10*v(t).unusedTokens.length,v(t).score=s,o?s<i&&(i=s,a=t):(null==i||s<i||r)&&(i=s,a=t,r&&(o=!0));h(e,a||t);}function Wa(e){if(!e._d){var t=ie(e._i),a=void 0===t.day?t.date:t.day;e._a=p([t.year,t.month,a,t.hour,t.minute,t.second,t.millisecond],function(e){return e&&parseInt(e,10);}),Ia(e);}}function Fa(e){var t=new k(ba(qa(e)));return t._nextDay&&(t.add(1,"d"),t._nextDay=void 0),t;}function qa(e){var t=e._i,a=e._f;return e._locale=e._locale||fa(e._l),null===t||void 0===a&&""===t?_({nullInput:!0}):("string"==typeof t&&(e._i=t=e._locale.preparse(t)),z(t)?new k(ba(t)):(c(t)?e._d=t:s(a)?Ra(e):a?Ba(e):Va(e),f(e)||(e._d=null),e));}function Va(e){var t=e._i;d(t)?e._d=new Date(i.now()):c(t)?e._d=new Date(t.valueOf()):"string"==typeof t?Pa(e):s(t)?(e._a=p(t.slice(0),function(e){return parseInt(e,10);}),Ia(e)):r(t)?Wa(e):u(t)?e._d=new Date(t):i.createFromInputFallback(e);}function Za(e,t,a,i,n){var o={};return!0!==t&&!1!==t||(i=t,t=void 0),!0!==a&&!1!==a||(i=a,a=void 0),(r(e)&&l(e)||s(e)&&0===e.length)&&(e=void 0),o._isAMomentObject=!0,o._useUTC=o._isUTC=n,o._l=a,o._i=e,o._f=t,o._strict=i,Fa(o);}function Ya(e,t,a,i){return Za(e,t,a,i,!1);}i.createFromInputFallback=x("value provided is not in a recognized RFC2822 or ISO format. moment construction falls back to js Date(), which is not reliable across all browsers and versions. Non RFC2822/ISO date formats are discouraged. Please refer to http://momentjs.com/guides/#/warnings/js-date/ for more info.",function(e){e._d=new Date(e._i+(e._useUTC?" UTC":""));}),i.ISO_8601=function(){},i.RFC_2822=function(){};var Ga=x("moment().min is deprecated, use moment.max instead. http://momentjs.com/guides/#/warnings/min-max/",function(){var e=Ya.apply(null,arguments);return this.isValid()&&e.isValid()?e<this?this:e:_();}),Ka=x("moment().max is deprecated, use moment.min instead. http://momentjs.com/guides/#/warnings/min-max/",function(){var e=Ya.apply(null,arguments);return this.isValid()&&e.isValid()?e>this?this:e:_();});function Xa(e,t){var a,i;if(1===t.length&&s(t[0])&&(t=t[0]),!t.length)return Ya();for(a=t[0],i=1;i<t.length;++i)t[i].isValid()&&!t[i][e](a)||(a=t[i]);return a;}function Ja(){return Xa("isBefore",[].slice.call(arguments,0));}function Qa(){return Xa("isAfter",[].slice.call(arguments,0));}var ei=function(){return Date.now?Date.now():+new Date();},ti=["year","quarter","month","week","day","hour","minute","second","millisecond"];function ai(e){var t,a,i=!1,n=ti.length;for(t in e)if(o(e,t)&&(-1===Ze.call(ti,t)||null!=e[t]&&isNaN(e[t])))return!1;for(a=0;a<n;++a)if(e[ti[a]]){if(i)return!1;parseFloat(e[ti[a]])!==De(e[ti[a]])&&(i=!0);}return!0;}function ii(){return this._isValid;}function ni(){return Ai(NaN);}function si(e){var t=ie(e),a=t.year||0,i=t.quarter||0,n=t.month||0,s=t.week||t.isoWeek||0,r=t.day||0,o=t.hour||0,l=t.minute||0,d=t.second||0,u=t.millisecond||0;this._isValid=ai(t),this._milliseconds=+u+1e3*d+6e4*l+1e3*o*60*60,this._days=+r+7*s,this._months=+n+3*i+12*a,this._data={},this._locale=fa(),this._bubble();}function ri(e){return e instanceof si;}function oi(e){return e<0?-1*Math.round(-1*e):Math.round(e);}function li(e,t,a){var i,n=Math.min(e.length,t.length),s=Math.abs(e.length-t.length),r=0;for(i=0;i<n;i++)(a&&e[i]!==t[i]||!a&&De(e[i])!==De(t[i]))&&r++;return r+s;}function di(e,t){B(e,0,0,function(){var e=this.utcOffset(),a="+";return e<0&&(e=-e,a="-"),a+P(~~(e/60),2)+t+P(~~e%60,2);});}di("Z",":"),di("ZZ",""),$e("Z",we),$e("ZZ",we),Oe(["Z","ZZ"],function(e,t,a){a._useUTC=!0,a._tzm=ci(we,e);});var ui=/([\+\-]|\d\d)/gi;function ci(e,t){var a,i,n=(t||"").match(e);return null===n?null:0===(i=60*(a=((n[n.length-1]||[])+"").match(ui)||["-",0,0])[1]+De(a[2]))?0:"+"===a[0]?i:-i;}function pi(e,t){var a,n;return t._isUTC?(a=t.clone(),n=(z(e)||c(e)?e.valueOf():Ya(e).valueOf())-a.valueOf(),a._d.setTime(a._d.valueOf()+n),i.updateOffset(a,!1),a):Ya(e).local();}function hi(e){return-Math.round(e._d.getTimezoneOffset());}function gi(e,t,a){var n,s=this._offset||0;if(!this.isValid())return null!=e?this:NaN;if(null!=e){if("string"==typeof e){if(null===(e=ci(we,e)))return this;}else Math.abs(e)<16&&!a&&(e*=60);return!this._isUTC&&t&&(n=hi(this)),this._offset=e,this._isUTC=!0,null!=n&&this.add(n,"m"),s!==e&&(!t||this._changeInProgress?ji(this,Ai(e-s,"m"),1,!1):this._changeInProgress||(this._changeInProgress=!0,i.updateOffset(this,!0),this._changeInProgress=null)),this;}return this._isUTC?s:hi(this);}function mi(e,t){return null!=e?("string"!=typeof e&&(e=-e),this.utcOffset(e,t),this):-this.utcOffset();}function vi(e){return this.utcOffset(0,e);}function fi(e){return this._isUTC&&(this.utcOffset(0,e),this._isUTC=!1,e&&this.subtract(hi(this),"m")),this;}function _i(){if(null!=this._tzm)this.utcOffset(this._tzm,!1,!0);else if("string"==typeof this._i){var e=ci(ye,this._i);null!=e?this.utcOffset(e):this.utcOffset(0,!0);}return this;}function bi(e){return!!this.isValid()&&(e=e?Ya(e).utcOffset():0,(this.utcOffset()-e)%60==0);}function yi(){return this.utcOffset()>this.clone().month(0).utcOffset()||this.utcOffset()>this.clone().month(5).utcOffset();}function wi(){if(!d(this._isDSTShifted))return this._isDSTShifted;var e,t={};return w(t,this),(t=qa(t))._a?(e=t._isUTC?g(t._a):Ya(t._a),this._isDSTShifted=this.isValid()&&li(t._a,e.toArray())>0):this._isDSTShifted=!1,this._isDSTShifted;}function ki(){return!!this.isValid()&&!this._isUTC;}function zi(){return!!this.isValid()&&this._isUTC;}function Si(){return!!this.isValid()&&this._isUTC&&0===this._offset;}i.updateOffset=function(){};var xi=/^(-|\+)?(?:(\d*)[. ])?(\d+):(\d+)(?::(\d+)(\.\d*)?)?$/,$i=/^(-|\+)?P(?:([-+]?[0-9,.]*)Y)?(?:([-+]?[0-9,.]*)M)?(?:([-+]?[0-9,.]*)W)?(?:([-+]?[0-9,.]*)D)?(?:T(?:([-+]?[0-9,.]*)H)?(?:([-+]?[0-9,.]*)M)?(?:([-+]?[0-9,.]*)S)?)?$/;function Ai(e,t){var a,i,n,s=e,r=null;return ri(e)?s={ms:e._milliseconds,d:e._days,M:e._months}:u(e)||!isNaN(+e)?(s={},t?s[t]=+e:s.milliseconds=+e):(r=xi.exec(e))?(a="-"===r[1]?-1:1,s={y:0,d:De(r[Le])*a,h:De(r[Be])*a,m:De(r[Ue])*a,s:De(r[Re])*a,ms:De(oi(1e3*r[We]))*a}):(r=$i.exec(e))?(a="-"===r[1]?-1:1,s={y:Mi(r[2],a),M:Mi(r[3],a),w:Mi(r[4],a),d:Mi(r[5],a),h:Mi(r[6],a),m:Mi(r[7],a),s:Mi(r[8],a)}):null==s?s={}:"object"==typeof s&&("from"in s||"to"in s)&&(n=Ti(Ya(s.from),Ya(s.to)),(s={}).ms=n.milliseconds,s.M=n.months),i=new si(s),ri(e)&&o(e,"_locale")&&(i._locale=e._locale),ri(e)&&o(e,"_isValid")&&(i._isValid=e._isValid),i;}function Mi(e,t){var a=e&&parseFloat(e.replace(",","."));return(isNaN(a)?0:a)*t;}function Ei(e,t){var a={};return a.months=t.month()-e.month()+12*(t.year()-e.year()),e.clone().add(a.months,"M").isAfter(t)&&--a.months,a.milliseconds=+t-+e.clone().add(a.months,"M"),a;}function Ti(e,t){var a;return e.isValid()&&t.isValid()?(t=pi(t,e),e.isBefore(t)?a=Ei(e,t):((a=Ei(t,e)).milliseconds=-a.milliseconds,a.months=-a.months),a):{milliseconds:0,months:0};}function Di(e,t){return function(a,i){var n;return null===i||isNaN(+i)||(M(t,"moment()."+t+"(period, number) is deprecated. Please use moment()."+t+"(number, period). See http://momentjs.com/guides/#/warnings/add-inverted-param/ for more info."),n=a,a=i,i=n),ji(this,Ai(a,i),e),this;};}function ji(e,t,a,n){var s=t._milliseconds,r=oi(t._days),o=oi(t._months);e.isValid()&&(n=null==n||n,o&&pt(e,Xe(e,"Month")+o*a),r&&Je(e,"Date",Xe(e,"Date")+r*a),s&&e._d.setTime(e._d.valueOf()+s*a),n&&i.updateOffset(e,r||o));}Ai.fn=si.prototype,Ai.invalid=ni;var Oi=Di(1,"add"),Ci=Di(-1,"subtract");function Pi(e){return"string"==typeof e||e instanceof String;}function Ni(e){return z(e)||c(e)||Pi(e)||u(e)||Ii(e)||Hi(e)||null==e;}function Hi(e){var t,a,i=r(e)&&!l(e),n=!1,s=["years","year","y","months","month","M","days","day","d","dates","date","D","hours","hour","h","minutes","minute","m","seconds","second","s","milliseconds","millisecond","ms"],d=s.length;for(t=0;t<d;t+=1)a=s[t],n=n||o(e,a);return i&&n;}function Ii(e){var t=s(e),a=!1;return t&&(a=0===e.filter(function(t){return!u(t)&&Pi(e);}).length),t&&a;}function Li(e){var t,a,i=r(e)&&!l(e),n=!1,s=["sameDay","nextDay","lastDay","nextWeek","lastWeek","sameElse"];for(t=0;t<s.length;t+=1)a=s[t],n=n||o(e,a);return i&&n;}function Bi(e,t){var a=e.diff(t,"days",!0);return a<-6?"sameElse":a<-1?"lastWeek":a<0?"lastDay":a<1?"sameDay":a<2?"nextDay":a<7?"nextWeek":"sameElse";}function Ui(e,t){1===arguments.length&&(arguments[0]?Ni(arguments[0])?(e=arguments[0],t=void 0):Li(arguments[0])&&(t=arguments[0],e=void 0):(e=void 0,t=void 0));var a=e||Ya(),n=pi(a,this).startOf("day"),s=i.calendarFormat(this,n)||"sameElse",r=t&&(E(t[s])?t[s].call(this,a):t[s]);return this.format(r||this.localeData().calendar(s,this,Ya(a)));}function Ri(){return new k(this);}function Wi(e,t){var a=z(e)?e:Ya(e);return!(!this.isValid()||!a.isValid())&&("millisecond"===(t=ae(t)||"millisecond")?this.valueOf()>a.valueOf():a.valueOf()<this.clone().startOf(t).valueOf());}function Fi(e,t){var a=z(e)?e:Ya(e);return!(!this.isValid()||!a.isValid())&&("millisecond"===(t=ae(t)||"millisecond")?this.valueOf()<a.valueOf():this.clone().endOf(t).valueOf()<a.valueOf());}function qi(e,t,a,i){var n=z(e)?e:Ya(e),s=z(t)?t:Ya(t);return!!(this.isValid()&&n.isValid()&&s.isValid())&&("("===(i=i||"()")[0]?this.isAfter(n,a):!this.isBefore(n,a))&&(")"===i[1]?this.isBefore(s,a):!this.isAfter(s,a));}function Vi(e,t){var a,i=z(e)?e:Ya(e);return!(!this.isValid()||!i.isValid())&&("millisecond"===(t=ae(t)||"millisecond")?this.valueOf()===i.valueOf():(a=i.valueOf(),this.clone().startOf(t).valueOf()<=a&&a<=this.clone().endOf(t).valueOf()));}function Zi(e,t){return this.isSame(e,t)||this.isAfter(e,t);}function Yi(e,t){return this.isSame(e,t)||this.isBefore(e,t);}function Gi(e,t,a){var i,n,s;if(!this.isValid())return NaN;if(!(i=pi(e,this)).isValid())return NaN;switch(n=6e4*(i.utcOffset()-this.utcOffset()),t=ae(t)){case"year":s=Ki(this,i)/12;break;case"month":s=Ki(this,i);break;case"quarter":s=Ki(this,i)/3;break;case"second":s=(this-i)/1e3;break;case"minute":s=(this-i)/6e4;break;case"hour":s=(this-i)/36e5;break;case"day":s=(this-i-n)/864e5;break;case"week":s=(this-i-n)/6048e5;break;default:s=this-i;}return a?s:Te(s);}function Ki(e,t){if(e.date()<t.date())return-Ki(t,e);var a=12*(t.year()-e.year())+(t.month()-e.month()),i=e.clone().add(a,"months");return-(a+(t-i<0?(t-i)/(i-e.clone().add(a-1,"months")):(t-i)/(e.clone().add(a+1,"months")-i)))||0;}function Xi(){return this.clone().locale("en").format("ddd MMM DD YYYY HH:mm:ss [GMT]ZZ");}function Ji(e){if(!this.isValid())return null;var t=!0!==e,a=t?this.clone().utc():this;return a.year()<0||a.year()>9999?W(a,t?"YYYYYY-MM-DD[T]HH:mm:ss.SSS[Z]":"YYYYYY-MM-DD[T]HH:mm:ss.SSSZ"):E(Date.prototype.toISOString)?t?this.toDate().toISOString():new Date(this.valueOf()+60*this.utcOffset()*1e3).toISOString().replace("Z",W(a,"Z")):W(a,t?"YYYY-MM-DD[T]HH:mm:ss.SSS[Z]":"YYYY-MM-DD[T]HH:mm:ss.SSSZ");}function Qi(){if(!this.isValid())return"moment.invalid(/* "+this._i+" */)";var e,t,a,i,n="moment",s="";return this.isLocal()||(n=0===this.utcOffset()?"moment.utc":"moment.parseZone",s="Z"),e="["+n+'("]',t=0<=this.year()&&this.year()<=9999?"YYYY":"YYYYYY",a="-MM-DD[T]HH:mm:ss.SSS",i=s+'[")]',this.format(e+t+a+i);}function en(e){e||(e=this.isUtc()?i.defaultFormatUtc:i.defaultFormat);var t=W(this,e);return this.localeData().postformat(t);}function tn(e,t){return this.isValid()&&(z(e)&&e.isValid()||Ya(e).isValid())?Ai({to:this,from:e}).locale(this.locale()).humanize(!t):this.localeData().invalidDate();}function an(e){return this.from(Ya(),e);}function nn(e,t){return this.isValid()&&(z(e)&&e.isValid()||Ya(e).isValid())?Ai({from:this,to:e}).locale(this.locale()).humanize(!t):this.localeData().invalidDate();}function sn(e){return this.to(Ya(),e);}function rn(e){var t;return void 0===e?this._locale._abbr:(null!=(t=fa(e))&&(this._locale=t),this);}i.defaultFormat="YYYY-MM-DDTHH:mm:ssZ",i.defaultFormatUtc="YYYY-MM-DDTHH:mm:ss[Z]";var on=x("moment().lang() is deprecated. Instead, use moment().localeData() to get the language configuration. Use moment().locale() to change languages.",function(e){return void 0===e?this.localeData():this.locale(e);});function ln(){return this._locale;}var dn=1e3,un=60*dn,cn=60*un,pn=3506328*cn;function hn(e,t){return(e%t+t)%t;}function gn(e,t,a){return e<100&&e>=0?new Date(e+400,t,a)-pn:new Date(e,t,a).valueOf();}function mn(e,t,a){return e<100&&e>=0?Date.UTC(e+400,t,a)-pn:Date.UTC(e,t,a);}function vn(e){var t,a;if(void 0===(e=ae(e))||"millisecond"===e||!this.isValid())return this;switch(a=this._isUTC?mn:gn,e){case"year":t=a(this.year(),0,1);break;case"quarter":t=a(this.year(),this.month()-this.month()%3,1);break;case"month":t=a(this.year(),this.month(),1);break;case"week":t=a(this.year(),this.month(),this.date()-this.weekday());break;case"isoWeek":t=a(this.year(),this.month(),this.date()-(this.isoWeekday()-1));break;case"day":case"date":t=a(this.year(),this.month(),this.date());break;case"hour":t=this._d.valueOf(),t-=hn(t+(this._isUTC?0:this.utcOffset()*un),cn);break;case"minute":t=this._d.valueOf(),t-=hn(t,un);break;case"second":t=this._d.valueOf(),t-=hn(t,dn);}return this._d.setTime(t),i.updateOffset(this,!0),this;}function fn(e){var t,a;if(void 0===(e=ae(e))||"millisecond"===e||!this.isValid())return this;switch(a=this._isUTC?mn:gn,e){case"year":t=a(this.year()+1,0,1)-1;break;case"quarter":t=a(this.year(),this.month()-this.month()%3+3,1)-1;break;case"month":t=a(this.year(),this.month()+1,1)-1;break;case"week":t=a(this.year(),this.month(),this.date()-this.weekday()+7)-1;break;case"isoWeek":t=a(this.year(),this.month(),this.date()-(this.isoWeekday()-1)+7)-1;break;case"day":case"date":t=a(this.year(),this.month(),this.date()+1)-1;break;case"hour":t=this._d.valueOf(),t+=cn-hn(t+(this._isUTC?0:this.utcOffset()*un),cn)-1;break;case"minute":t=this._d.valueOf(),t+=un-hn(t,un)-1;break;case"second":t=this._d.valueOf(),t+=dn-hn(t,dn)-1;}return this._d.setTime(t),i.updateOffset(this,!0),this;}function _n(){return this._d.valueOf()-6e4*(this._offset||0);}function bn(){return Math.floor(this.valueOf()/1e3);}function yn(){return new Date(this.valueOf());}function wn(){var e=this;return[e.year(),e.month(),e.date(),e.hour(),e.minute(),e.second(),e.millisecond()];}function kn(){var e=this;return{years:e.year(),months:e.month(),date:e.date(),hours:e.hours(),minutes:e.minutes(),seconds:e.seconds(),milliseconds:e.milliseconds()};}function zn(){return this.isValid()?this.toISOString():null;}function Sn(){return f(this);}function xn(){return h({},v(this));}function $n(){return v(this).overflow;}function An(){return{input:this._i,format:this._f,locale:this._locale,isUTC:this._isUTC,strict:this._strict};}function Mn(e,t){var a,n,s,r=this._eras||fa("en")._eras;for(a=0,n=r.length;a<n;++a)switch("string"==typeof r[a].since&&(s=i(r[a].since).startOf("day"),r[a].since=s.valueOf()),typeof r[a].until){case"undefined":r[a].until=1/0;break;case"string":s=i(r[a].until).startOf("day").valueOf(),r[a].until=s.valueOf();}return r;}function En(e,t,a){var i,n,s,r,o,l=this.eras();for(e=e.toUpperCase(),i=0,n=l.length;i<n;++i)if(s=l[i].name.toUpperCase(),r=l[i].abbr.toUpperCase(),o=l[i].narrow.toUpperCase(),a)switch(t){case"N":case"NN":case"NNN":if(r===e)return l[i];break;case"NNNN":if(s===e)return l[i];break;case"NNNNN":if(o===e)return l[i];}else if([s,r,o].indexOf(e)>=0)return l[i];}function Tn(e,t){var a=e.since<=e.until?1:-1;return void 0===t?i(e.since).year():i(e.since).year()+(t-e.offset)*a;}function Dn(){var e,t,a,i=this.localeData().eras();for(e=0,t=i.length;e<t;++e){if(a=this.clone().startOf("day").valueOf(),i[e].since<=a&&a<=i[e].until)return i[e].name;if(i[e].until<=a&&a<=i[e].since)return i[e].name;}return"";}function jn(){var e,t,a,i=this.localeData().eras();for(e=0,t=i.length;e<t;++e){if(a=this.clone().startOf("day").valueOf(),i[e].since<=a&&a<=i[e].until)return i[e].narrow;if(i[e].until<=a&&a<=i[e].since)return i[e].narrow;}return"";}function On(){var e,t,a,i=this.localeData().eras();for(e=0,t=i.length;e<t;++e){if(a=this.clone().startOf("day").valueOf(),i[e].since<=a&&a<=i[e].until)return i[e].abbr;if(i[e].until<=a&&a<=i[e].since)return i[e].abbr;}return"";}function Cn(){var e,t,a,n,s=this.localeData().eras();for(e=0,t=s.length;e<t;++e)if(a=s[e].since<=s[e].until?1:-1,n=this.clone().startOf("day").valueOf(),s[e].since<=n&&n<=s[e].until||s[e].until<=n&&n<=s[e].since)return(this.year()-i(s[e].since).year())*a+s[e].offset;return this.year();}function Pn(e){return o(this,"_erasNameRegex")||Rn.call(this),e?this._erasNameRegex:this._erasRegex;}function Nn(e){return o(this,"_erasAbbrRegex")||Rn.call(this),e?this._erasAbbrRegex:this._erasRegex;}function Hn(e){return o(this,"_erasNarrowRegex")||Rn.call(this),e?this._erasNarrowRegex:this._erasRegex;}function In(e,t){return t.erasAbbrRegex(e);}function Ln(e,t){return t.erasNameRegex(e);}function Bn(e,t){return t.erasNarrowRegex(e);}function Un(e,t){return t._eraYearOrdinalRegex||_e;}function Rn(){var e,t,a,i,n,s=[],r=[],o=[],l=[],d=this.eras();for(e=0,t=d.length;e<t;++e)a=Ee(d[e].name),i=Ee(d[e].abbr),n=Ee(d[e].narrow),r.push(a),s.push(i),o.push(n),l.push(a),l.push(i),l.push(n);this._erasRegex=new RegExp("^("+l.join("|")+")","i"),this._erasNameRegex=new RegExp("^("+r.join("|")+")","i"),this._erasAbbrRegex=new RegExp("^("+s.join("|")+")","i"),this._erasNarrowRegex=new RegExp("^("+o.join("|")+")","i");}function Wn(e,t){B(0,[e,e.length],0,t);}function Fn(e){return Kn.call(this,e,this.week(),this.weekday()+this.localeData()._week.dow,this.localeData()._week.dow,this.localeData()._week.doy);}function qn(e){return Kn.call(this,e,this.isoWeek(),this.isoWeekday(),1,4);}function Vn(){return zt(this.year(),1,4);}function Zn(){return zt(this.isoWeekYear(),1,4);}function Yn(){var e=this.localeData()._week;return zt(this.year(),e.dow,e.doy);}function Gn(){var e=this.localeData()._week;return zt(this.weekYear(),e.dow,e.doy);}function Kn(e,t,a,i,n){var s;return null==e?kt(this,i,n).year:(t>(s=zt(e,i,n))&&(t=s),Xn.call(this,e,t,a,i,n));}function Xn(e,t,a,i,n){var s=wt(e,t,a,i,n),r=bt(s.year,0,s.dayOfYear);return this.year(r.getUTCFullYear()),this.month(r.getUTCMonth()),this.date(r.getUTCDate()),this;}function Jn(e){return null==e?Math.ceil((this.month()+1)/3):this.month(3*(e-1)+this.month()%3);}B("N",0,0,"eraAbbr"),B("NN",0,0,"eraAbbr"),B("NNN",0,0,"eraAbbr"),B("NNNN",0,0,"eraName"),B("NNNNN",0,0,"eraNarrow"),B("y",["y",1],"yo","eraYear"),B("y",["yy",2],0,"eraYear"),B("y",["yyy",3],0,"eraYear"),B("y",["yyyy",4],0,"eraYear"),$e("N",In),$e("NN",In),$e("NNN",In),$e("NNNN",Ln),$e("NNNNN",Bn),Oe(["N","NN","NNN","NNNN","NNNNN"],function(e,t,a,i){var n=a._locale.erasParse(e,i,a._strict);n?v(a).era=n:v(a).invalidEra=e;}),$e("y",_e),$e("yy",_e),$e("yyy",_e),$e("yyyy",_e),$e("yo",Un),Oe(["y","yy","yyy","yyyy"],He),Oe(["yo"],function(e,t,a,i){var n;a._locale._eraYearOrdinalRegex&&(n=e.match(a._locale._eraYearOrdinalRegex)),a._locale.eraYearOrdinalParse?t[He]=a._locale.eraYearOrdinalParse(e,n):t[He]=parseInt(e,10);}),B(0,["gg",2],0,function(){return this.weekYear()%100;}),B(0,["GG",2],0,function(){return this.isoWeekYear()%100;}),Wn("gggg","weekYear"),Wn("ggggg","weekYear"),Wn("GGGG","isoWeekYear"),Wn("GGGGG","isoWeekYear"),$e("G",be),$e("g",be),$e("GG",pe,le),$e("gg",pe,le),$e("GGGG",ve,ue),$e("gggg",ve,ue),$e("GGGGG",fe,ce),$e("ggggg",fe,ce),Ce(["gggg","ggggg","GGGG","GGGGG"],function(e,t,a,i){t[i.substr(0,2)]=De(e);}),Ce(["gg","GG"],function(e,t,a,n){t[n]=i.parseTwoDigitYear(e);}),B("Q",0,"Qo","quarter"),$e("Q",oe),Oe("Q",function(e,t){t[Ie]=3*(De(e)-1);}),B("D",["DD",2],"Do","date"),$e("D",pe,Se),$e("DD",pe,le),$e("Do",function(e,t){return e?t._dayOfMonthOrdinalParse||t._ordinalParse:t._dayOfMonthOrdinalParseLenient;}),Oe(["D","DD"],Le),Oe("Do",function(e,t){t[Le]=De(e.match(pe)[0]);});var Qn=Ke("Date",!0);function es(e){var t=Math.round((this.clone().startOf("day")-this.clone().startOf("year"))/864e5)+1;return null==e?t:this.add(e-t,"d");}B("DDD",["DDDD",3],"DDDo","dayOfYear"),$e("DDD",me),$e("DDDD",de),Oe(["DDD","DDDD"],function(e,t,a){a._dayOfYear=De(e);}),B("m",["mm",2],0,"minute"),$e("m",pe,xe),$e("mm",pe,le),Oe(["m","mm"],Ue);var ts=Ke("Minutes",!1);B("s",["ss",2],0,"second"),$e("s",pe,xe),$e("ss",pe,le),Oe(["s","ss"],Re);var as,is,ns=Ke("Seconds",!1);for(B("S",0,0,function(){return~~(this.millisecond()/100);}),B(0,["SS",2],0,function(){return~~(this.millisecond()/10);}),B(0,["SSS",3],0,"millisecond"),B(0,["SSSS",4],0,function(){return 10*this.millisecond();}),B(0,["SSSSS",5],0,function(){return 100*this.millisecond();}),B(0,["SSSSSS",6],0,function(){return 1e3*this.millisecond();}),B(0,["SSSSSSS",7],0,function(){return 1e4*this.millisecond();}),B(0,["SSSSSSSS",8],0,function(){return 1e5*this.millisecond();}),B(0,["SSSSSSSSS",9],0,function(){return 1e6*this.millisecond();}),$e("S",me,oe),$e("SS",me,le),$e("SSS",me,de),as="SSSS";as.length<=9;as+="S")$e(as,_e);function ss(e,t){t[We]=De(1e3*("0."+e));}for(as="S";as.length<=9;as+="S")Oe(as,ss);function rs(){return this._isUTC?"UTC":"";}function os(){return this._isUTC?"Coordinated Universal Time":"";}is=Ke("Milliseconds",!1),B("z",0,0,"zoneAbbr"),B("zz",0,0,"zoneName");var ls=k.prototype;function ds(e){return Ya(1e3*e);}function us(){return Ya.apply(null,arguments).parseZone();}function cs(e){return e;}ls.add=Oi,ls.calendar=Ui,ls.clone=Ri,ls.diff=Gi,ls.endOf=fn,ls.format=en,ls.from=tn,ls.fromNow=an,ls.to=nn,ls.toNow=sn,ls.get=Qe,ls.invalidAt=$n,ls.isAfter=Wi,ls.isBefore=Fi,ls.isBetween=qi,ls.isSame=Vi,ls.isSameOrAfter=Zi,ls.isSameOrBefore=Yi,ls.isValid=Sn,ls.lang=on,ls.locale=rn,ls.localeData=ln,ls.max=Ka,ls.min=Ga,ls.parsingFlags=xn,ls.set=et,ls.startOf=vn,ls.subtract=Ci,ls.toArray=wn,ls.toObject=kn,ls.toDate=yn,ls.toISOString=Ji,ls.inspect=Qi,"undefined"!=typeof Symbol&&null!=Symbol.for&&(ls[Symbol.for("nodejs.util.inspect.custom")]=function(){return"Moment<"+this.format()+">";}),ls.toJSON=zn,ls.toString=Xi,ls.unix=bn,ls.valueOf=_n,ls.creationData=An,ls.eraName=Dn,ls.eraNarrow=jn,ls.eraAbbr=On,ls.eraYear=Cn,ls.year=Ye,ls.isLeapYear=Ge,ls.weekYear=Fn,ls.isoWeekYear=qn,ls.quarter=ls.quarters=Jn,ls.month=ht,ls.daysInMonth=gt,ls.week=ls.weeks=Mt,ls.isoWeek=ls.isoWeeks=Et,ls.weeksInYear=Yn,ls.weeksInWeekYear=Gn,ls.isoWeeksInYear=Vn,ls.isoWeeksInISOWeekYear=Zn,ls.date=Qn,ls.day=ls.days=Ft,ls.weekday=qt,ls.isoWeekday=Vt,ls.dayOfYear=es,ls.hour=ls.hours=ia,ls.minute=ls.minutes=ts,ls.second=ls.seconds=ns,ls.millisecond=ls.milliseconds=is,ls.utcOffset=gi,ls.utc=vi,ls.local=fi,ls.parseZone=_i,ls.hasAlignedHourOffset=bi,ls.isDST=yi,ls.isLocal=ki,ls.isUtcOffset=zi,ls.isUtc=Si,ls.isUTC=Si,ls.zoneAbbr=rs,ls.zoneName=os,ls.dates=x("dates accessor is deprecated. Use date instead.",Qn),ls.months=x("months accessor is deprecated. Use month instead",ht),ls.years=x("years accessor is deprecated. Use year instead",Ye),ls.zone=x("moment().zone is deprecated, use moment().utcOffset instead. http://momentjs.com/guides/#/warnings/zone/",mi),ls.isDSTShifted=x("isDSTShifted is deprecated. See http://momentjs.com/guides/#/warnings/dst-shifted/ for more information",wi);var ps=j.prototype;function hs(e,t,a,i){var n=fa(),s=g().set(i,t);return n[a](s,e);}function gs(e,t,a){if(u(e)&&(t=e,e=void 0),e=e||"",null!=t)return hs(e,t,a,"month");var i,n=[];for(i=0;i<12;i++)n[i]=hs(e,i,a,"month");return n;}function ms(e,t,a,i){"boolean"==typeof e?(u(t)&&(a=t,t=void 0),t=t||""):(a=t=e,e=!1,u(t)&&(a=t,t=void 0),t=t||"");var n,s=fa(),r=e?s._week.dow:0,o=[];if(null!=a)return hs(t,(a+r)%7,i,"day");for(n=0;n<7;n++)o[n]=hs(t,(n+r)%7,i,"day");return o;}function vs(e,t){return gs(e,t,"months");}function fs(e,t){return gs(e,t,"monthsShort");}function _s(e,t,a){return ms(e,t,a,"weekdays");}function bs(e,t,a){return ms(e,t,a,"weekdaysShort");}function ys(e,t,a){return ms(e,t,a,"weekdaysMin");}ps.calendar=C,ps.longDateFormat=V,ps.invalidDate=Y,ps.ordinal=X,ps.preparse=cs,ps.postformat=cs,ps.relativeTime=Q,ps.pastFuture=ee,ps.set=T,ps.eras=Mn,ps.erasParse=En,ps.erasConvertYear=Tn,ps.erasAbbrRegex=Nn,ps.erasNameRegex=Pn,ps.erasNarrowRegex=Hn,ps.months=lt,ps.monthsShort=dt,ps.monthsParse=ct,ps.monthsRegex=vt,ps.monthsShortRegex=mt,ps.week=St,ps.firstDayOfYear=At,ps.firstDayOfWeek=$t,ps.weekdays=Lt,ps.weekdaysMin=Ut,ps.weekdaysShort=Bt,ps.weekdaysParse=Wt,ps.weekdaysRegex=Zt,ps.weekdaysShortRegex=Yt,ps.weekdaysMinRegex=Gt,ps.isPM=ta,ps.meridiem=na,ga("en",{eras:[{since:"0001-01-01",until:1/0,offset:1,name:"Anno Domini",narrow:"AD",abbr:"AD"},{since:"0000-12-31",until:-1/0,offset:1,name:"Before Christ",narrow:"BC",abbr:"BC"}],dayOfMonthOrdinalParse:/\d{1,2}(th|st|nd|rd)/,ordinal:function(e){var t=e%10;return e+(1===De(e%100/10)?"th":1===t?"st":2===t?"nd":3===t?"rd":"th");}}),i.lang=x("moment.lang is deprecated. Use moment.locale instead.",ga),i.langData=x("moment.langData is deprecated. Use moment.localeData instead.",fa);var ws=Math.abs;function ks(){var e=this._data;return this._milliseconds=ws(this._milliseconds),this._days=ws(this._days),this._months=ws(this._months),e.milliseconds=ws(e.milliseconds),e.seconds=ws(e.seconds),e.minutes=ws(e.minutes),e.hours=ws(e.hours),e.months=ws(e.months),e.years=ws(e.years),this;}function zs(e,t,a,i){var n=Ai(t,a);return e._milliseconds+=i*n._milliseconds,e._days+=i*n._days,e._months+=i*n._months,e._bubble();}function Ss(e,t){return zs(this,e,t,1);}function xs(e,t){return zs(this,e,t,-1);}function $s(e){return e<0?Math.floor(e):Math.ceil(e);}function As(){var e,t,a,i,n,s=this._milliseconds,r=this._days,o=this._months,l=this._data;return s>=0&&r>=0&&o>=0||s<=0&&r<=0&&o<=0||(s+=864e5*$s(Es(o)+r),r=0,o=0),l.milliseconds=s%1e3,e=Te(s/1e3),l.seconds=e%60,t=Te(e/60),l.minutes=t%60,a=Te(t/60),l.hours=a%24,r+=Te(a/24),o+=n=Te(Ms(r)),r-=$s(Es(n)),i=Te(o/12),o%=12,l.days=r,l.months=o,l.years=i,this;}function Ms(e){return 4800*e/146097;}function Es(e){return 146097*e/4800;}function Ts(e){if(!this.isValid())return NaN;var t,a,i=this._milliseconds;if("month"===(e=ae(e))||"quarter"===e||"year"===e)switch(t=this._days+i/864e5,a=this._months+Ms(t),e){case"month":return a;case"quarter":return a/3;case"year":return a/12;}else switch(t=this._days+Math.round(Es(this._months)),e){case"week":return t/7+i/6048e5;case"day":return t+i/864e5;case"hour":return 24*t+i/36e5;case"minute":return 1440*t+i/6e4;case"second":return 86400*t+i/1e3;case"millisecond":return Math.floor(864e5*t)+i;default:throw new Error("Unknown unit "+e);}}function Ds(e){return function(){return this.as(e);};}var js=Ds("ms"),Os=Ds("s"),Cs=Ds("m"),Ps=Ds("h"),Ns=Ds("d"),Hs=Ds("w"),Is=Ds("M"),Ls=Ds("Q"),Bs=Ds("y"),Us=js;function Rs(){return Ai(this);}function Ws(e){return e=ae(e),this.isValid()?this[e+"s"]():NaN;}function Fs(e){return function(){return this.isValid()?this._data[e]:NaN;};}var qs=Fs("milliseconds"),Vs=Fs("seconds"),Zs=Fs("minutes"),Ys=Fs("hours"),Gs=Fs("days"),Ks=Fs("months"),Xs=Fs("years");function Js(){return Te(this.days()/7);}var Qs=Math.round,er={ss:44,s:45,m:45,h:22,d:26,w:null,M:11};function tr(e,t,a,i,n){return n.relativeTime(t||1,!!a,e,i);}function ar(e,t,a,i){var n=Ai(e).abs(),s=Qs(n.as("s")),r=Qs(n.as("m")),o=Qs(n.as("h")),l=Qs(n.as("d")),d=Qs(n.as("M")),u=Qs(n.as("w")),c=Qs(n.as("y")),p=s<=a.ss&&["s",s]||s<a.s&&["ss",s]||r<=1&&["m"]||r<a.m&&["mm",r]||o<=1&&["h"]||o<a.h&&["hh",o]||l<=1&&["d"]||l<a.d&&["dd",l];return null!=a.w&&(p=p||u<=1&&["w"]||u<a.w&&["ww",u]),(p=p||d<=1&&["M"]||d<a.M&&["MM",d]||c<=1&&["y"]||["yy",c])[2]=t,p[3]=+e>0,p[4]=i,tr.apply(null,p);}function ir(e){return void 0===e?Qs:"function"==typeof e&&(Qs=e,!0);}function sr(e,t){return void 0!==er[e]&&(void 0===t?er[e]:(er[e]=t,"s"===e&&(er.ss=t-1),!0));}function rr(e,t){if(!this.isValid())return this.localeData().invalidDate();var a,i,n=!1,s=er;return"object"==typeof e&&(t=e,e=!1),"boolean"==typeof e&&(n=e),"object"==typeof t&&(s=Object.assign({},er,t),null!=t.s&&null==t.ss&&(s.ss=t.s-1)),i=ar(this,!n,s,a=this.localeData()),n&&(i=a.pastFuture(+this,i)),a.postformat(i);}var or=Math.abs;function lr(e){return(e>0)-(e<0)||+e;}function dr(){if(!this.isValid())return this.localeData().invalidDate();var e,t,a,i,n,s,r,o,l=or(this._milliseconds)/1e3,d=or(this._days),u=or(this._months),c=this.asSeconds();return c?(e=Te(l/60),t=Te(e/60),l%=60,e%=60,a=Te(u/12),u%=12,i=l?l.toFixed(3).replace(/\.?0+$/,""):"",n=c<0?"-":"",s=lr(this._months)!==lr(c)?"-":"",r=lr(this._days)!==lr(c)?"-":"",o=lr(this._milliseconds)!==lr(c)?"-":"",n+"P"+(a?s+a+"Y":"")+(u?s+u+"M":"")+(d?r+d+"D":"")+(t||e||l?"T":"")+(t?o+t+"H":"")+(e?o+e+"M":"")+(l?o+i+"S":"")):"P0D";}var ur=si.prototype;return ur.isValid=ii,ur.abs=ks,ur.add=Ss,ur.subtract=xs,ur.as=Ts,ur.asMilliseconds=js,ur.asSeconds=Os,ur.asMinutes=Cs,ur.asHours=Ps,ur.asDays=Ns,ur.asWeeks=Hs,ur.asMonths=Is,ur.asQuarters=Ls,ur.asYears=Bs,ur.valueOf=Us,ur._bubble=As,ur.clone=Rs,ur.get=Ws,ur.milliseconds=qs,ur.seconds=Vs,ur.minutes=Zs,ur.hours=Ys,ur.days=Gs,ur.weeks=Js,ur.months=Ks,ur.years=Xs,ur.humanize=rr,ur.toISOString=dr,ur.toString=dr,ur.toJSON=dr,ur.locale=rn,ur.localeData=ln,ur.toIsoString=x("toIsoString() is deprecated. Please use toISOString() instead (notice the capitals)",dr),ur.lang=on,B("X",0,0,"unix"),B("x",0,0,"valueOf"),$e("x",be),$e("X",ke),Oe("X",function(e,t,a){a._d=new Date(1e3*parseFloat(e));}),Oe("x",function(e,t,a){a._d=new Date(De(e));}),//! moment.js
i.version="2.30.1",n(Ya),i.fn=ls,i.min=Ja,i.max=Qa,i.now=ei,i.utc=g,i.unix=ds,i.months=vs,i.isDate=c,i.locale=ga,i.invalid=_,i.duration=Ai,i.isMoment=z,i.weekdays=_s,i.parseZone=us,i.localeData=fa,i.isDuration=ri,i.monthsShort=fs,i.weekdaysMin=ys,i.defineLocale=ma,i.updateLocale=va,i.locales=_a,i.weekdaysShort=bs,i.normalizeUnits=ae,i.relativeTimeRounding=ir,i.relativeTimeThreshold=sr,i.calendarFormat=Bi,i.prototype=ls,i.HTML5_FMT={DATETIME_LOCAL:"YYYY-MM-DDTHH:mm",DATETIME_LOCAL_SECONDS:"YYYY-MM-DDTHH:mm:ss",DATETIME_LOCAL_MS:"YYYY-MM-DDTHH:mm:ss.SSS",DATE:"YYYY-MM-DD",TIME:"HH:mm",TIME_SECONDS:"HH:mm:ss",TIME_MS:"HH:mm:ss.SSS",WEEK:"GGGG-[W]WW",MONTH:"YYYY-MM"},i;}();}(rr)),rr.exports),lr=ir(or);let dr=class extends de{constructor(){super(...arguments),this.label="",this.unit="",this.help="",this.required=!1,this._helpOpen=!1;}_toggleHelp(){this._helpOpen=!this._helpOpen;}render(){return W`
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
    `;}static get styles(){return c`
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
    `;}};n([he()],dr.prototype,"label",void 0),n([he()],dr.prototype,"unit",void 0),n([he()],dr.prototype,"help",void 0),n([he({type:Boolean})],dr.prototype,"required",void 0),n([ge()],dr.prototype,"_helpOpen",void 0),dr=n([ce("si-field")],dr);let ur=class extends Qs(de){constructor(){super(...arguments),this.zones=[],this.modules=[],this.mappings=[],this.wateringCalendars=new Map(),this.weatherRecords=new Map(),this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._showAddZone=!1,this._operationError=null,this._confirmIrrigate=null,this._confirmDeleteZoneId=null,this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._updateScheduled=!1,this.globalDebounceTimer=null;}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate();}));}firstUpdated(){be().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate();});}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e);}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e);});},{type:Se+"_config_updated"})];}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;try{e&&(this.isLoading=!0);const[t,a,i,n]=await Promise.all([Us(this.hass),Rs(this.hass),Fs(this.hass),Zs(this.hass)]);this.config=t,this.zones=a,this.modules=i,this.mappings=n,this._initialLoadDone=!0,this._fetchWateringCalendars(),this._fetchWeatherRecords();}catch(e){console.error("Error fetching data:",e),Ns(this,this.hass,"common.errors.load_failed",e);}finally{e&&(this.isLoading=!1),this._scheduleUpdate();}}handleCalculateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",Se+"/zones",{calculate_all:!0})).catch(e=>{console.error("Failed to calculate all zones:",e),Ns(this,this.hass,"common.errors.action_failed",e);}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc-all:",e));}));}handleUpdateAllZones(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",Se+"/zones",{update_all:!0})).catch(e=>{console.error("Failed to update all zones:",e),Ns(this,this.hass,"common.errors.action_failed",e);}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update-all:",e));}));}handleResetAllBuckets(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",Se+"/zones",{reset_all_buckets:!0})).catch(e=>{console.error("Failed to reset all buckets:",e),Ns(this,this.hass,"common.errors.action_failed",e);}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after reset:",e));}));}handleClearAllWeatherdata(){var e;this.hass&&(this.isSaving=!0,this._scheduleUpdate(),(e=this.hass,e.callApi("POST",Se+"/zones",{clear_all_weatherdata:!0})).catch(e=>{console.error("Failed to clear all weather data:",e),Ns(this,this.hass,"common.errors.action_failed",e);}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after clear-weather:",e));}));}handleAddZone(){if(!this._newZoneName.trim())return;const e={name:this._newZoneName.trim(),size:Math.round(100*(parseFloat(this._newZoneSize)||0))/100,throughput:Math.round(100*(parseFloat(this._newZoneThroughput)||0))/100,state:tr.Automatic,duration:0,bucket:0,module:void 0,delta:0,explanation:"",multiplier:1,mapping:void 0,lead_time:0,maximum_duration:void 0,maximum_bucket:void 0,drainage_rate:void 0,current_drainage:0};this.zones=[...this.zones,e],this.isSaving=!0,this._showAddZone=!1,this.saveToHA(e).then(()=>(this._newZoneName="",this._newZoneSize="",this._newZoneThroughput="",this._fetchData())).catch(e=>{console.error("Failed to add zone:",e),this.zones=this.zones.slice(0,-1),Ns(this,this.hass,"common.errors.save_failed",e);}).finally(()=>{this.isSaving=!1,this._scheduleUpdate();});}handleEditZone(e,t){this.hass&&(this.zones=this.zones.map((a,i)=>i===e?t:a),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this.saveToHA(t).catch(e=>{console.error("Failed to save zone:",e),Ns(this,this.hass,"common.errors.save_failed",e);}).finally(()=>{this.isSaving=!1,this._scheduleUpdate();}),this.globalDebounceTimer=null;},500),this._scheduleUpdate());}handleRemoveZone(e){this._confirmDeleteZoneId=e;}_confirmDelete(){const e=this._confirmDeleteZoneId;if(null===e||!this.hass)return;const t=this.zones.findIndex(t=>t.id===e);if(-1===t)return;const a=[...this.zones];var i,n;this.zones=this.zones.filter(t=>t.id!==e),this._confirmDeleteZoneId=null,this.isSaving=!0,(i=this.hass,n=e.toString(),i.callApi("POST",Se+"/zones",{id:n,remove:!0})).catch(e=>{console.error("Failed to delete zone:",e),Ns(this,this.hass,"common.errors.delete_failed",e),this.zones=a,this._fetchData().catch(e=>console.error("Failed to refresh data after delete error:",e));}).finally(()=>{this.isSaving=!1,this._scheduleUpdate();});}get _linkedZoneCount(){return this.zones.filter(e=>{var t;return e.linked_entity&&(null!==(t=e.duration)&&void 0!==t?t:0)>0;}).length;}async _doIrrigate(){var e;const t=this._confirmIrrigate;if(this._confirmIrrigate=null,null===t||!this.hass)return;const a="all"===t,i=a?void 0:this.zones.find(e=>{var a;return(null===(a=e.id)||void 0===a?void 0:a.toString())===t;}),n=a?`(${this._linkedZoneCount})`:`: ${null!==(e=null==i?void 0:i.name)&&void 0!==e?e:t}`;try{await(s=this.hass,r=a?void 0:t,s.callWS(Object.assign({type:Se+"/irrigate_now"},void 0!==r?{zone_id:r}:{}))),Ps(this,`${Es("panels.zones.confirm_irrigate.toast_started",this.hass.language)} ${n}`);}catch(e){const t=Cs(e);console.error("irrigate_now failed",e),Ps(this,`${Es("panels.zones.confirm_irrigate.toast_failed",this.hass.language)}: ${t}`);}var s,r;}handleCalculateZone(e){const t=this.zones[e];var a,i;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(a=this.hass,i=t.id.toString(),a.callApi("POST",Se+"/zones",{id:i,calculate:!0,override_cache:!0})).catch(e=>{const t=Cs(e);console.error("calculateZone failed:",e),this._operationError=t;}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after calc:",e));}));}handleUpdateZone(e){const t=this.zones[e];var a,i;t&&null!=t.id&&this.hass&&(this._operationError=null,this.isSaving=!0,this._scheduleUpdate(),(a=this.hass,i=t.id.toString(),a.callApi("POST",Se+"/zones",{id:i,update:!0})).catch(e=>{const t=Cs(e);console.error("updateZone failed:",e),this._operationError=t;}).finally(()=>{this.isSaving=!1,this._fetchData().catch(e=>console.error("fetchData after update:",e));}));}async _fetchWeatherRecords(){if(this.hass){for(const e of this.zones)if(void 0!==e.id&&void 0!==e.mapping)try{const t=await Gs(this.hass,e.mapping.toString(),0);this.weatherRecords.set(e.id,t);}catch(t){console.error(`Failed to fetch weather records for zone ${e.id}:`,t);}this._scheduleUpdate();}}async _fetchWateringCalendars(){if(this.hass){for(const a of this.zones)if(void 0!==a.id)try{const i=await(e=this.hass,t=a.id.toString(),e.callWS({type:Se+"/watering_calendar",zone_id:t}));this.wateringCalendars.set(a.id,i);}catch(e){console.error(`Failed to fetch watering calendar for zone ${a.id}:`,e);}var e,t;this._scheduleUpdate();}}renderWeatherRecords(e){if(!this.hass||"number"!=typeof e.id)return W``;const t=this.weatherRecords.get(e.id)||[];return W`
      <div class="card-content">
        ${0===t.length?W`
              <div class="weather-note">
                ${Es("panels.mappings.weather-records.no-data",this.hass.language)}
              </div>
            `:W`
              <div class="weather-table">
                <div class="weather-header">
                  <span
                    >${Es("panels.mappings.weather-records.timestamp",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.temperature",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.humidity",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.dewpoint",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.wind",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.pressure",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.precipitation",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.retrieval-time",this.hass.language)}</span
                  >
                </div>
                ${t.map(e=>{const t=e=>{try{const t=lr(e);return t.isValid()?t.format("MM-DD HH:mm"):"-";}catch(e){return"-";}},a=(e,t,a=1)=>null!=e?e.toFixed(a)+t:"-";return W`
                    <div class="weather-row">
                      <span>${t(e.timestamp)}</span>
                      <span>${a(e.temperature,"°C")}</span>
                      <span>${a(e.humidity,"%")}</span>
                      <span>${a(e.dewpoint,"°C")}</span>
                      <span>${a(e.wind_speed,"m/s")}</span>
                      <span>${a(e.pressure,"hPa",0)}</span>
                      <span>${a(e.precipitation,"mm")}</span>
                      <span>${t(e.retrieval_time)}</span>
                    </div>
                  `;})}
              </div>
            `}
      </div>
    `;}renderWateringCalendar(e){if(!this.hass||"number"!=typeof e.id)return W``;const t=this.wateringCalendars.get(e.id),a=t&&e.id in t?t[e.id]:null,i=(null==a?void 0:a.monthly_estimates)||[];return W`
      <div class="card-content">
        ${0===i.length?W`
              <div class="calendar-note">
                ${(null==a?void 0:a.error)?`Error generating calendar: ${a.error}`:"No watering calendar data available for this zone"}
              </div>
            `:W`
              <div class="calendar-table">
                <div class="calendar-header">
                  <span>Month</span>
                  <span>ET (mm)</span>
                  <span>Precipitation (mm)</span>
                  <span>Watering (L)</span>
                  <span>Avg Temp (°C)</span>
                </div>
                ${i.map(e=>W`
                    <div class="calendar-row">
                      <span
                        >${e.month_name||`Month ${e.month}`||"-"}</span
                      >
                      <span
                        >${e.estimated_et_mm?e.estimated_et_mm.toFixed(1):"-"}</span
                      >
                      <span
                        >${e.average_precipitation_mm?e.average_precipitation_mm.toFixed(1):"-"}</span
                      >
                      <span
                        >${e.estimated_watering_volume_liters?e.estimated_watering_volume_liters.toFixed(0):"-"}</span
                      >
                      <span
                        >${e.average_temperature_c?e.average_temperature_c.toFixed(1):"-"}</span
                      >
                    </div>
                  `)}
              </div>
              ${(null==a?void 0:a.calculation_method)?W`
                    <div class="calendar-info">
                      Method: ${a.calculation_method}
                    </div>
                  `:""}
            `}
      </div>
    `;}async saveToHA(e){if(!this.hass)throw new Error("Home Assistant connection not available");await Ws(this.hass,e);}_renderModuleOptions(e){if(!this.hass)return W``;const t=null!=e?String(e):"";return W`
      <option value="" ?selected="${""===t}">
        ---${Es("common.labels.select",this.hass.language)}---
      </option>
      ${this.modules.map(e=>W`
          <option value="${e.id}" ?selected="${t===String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `;}_renderMappingOptions(e){if(!this.hass)return W``;const t=null!=e?String(e):"";return W`
      <option value="" ?selected="${""===t}">
        ---${Es("common.labels.select",this.hass.language)}---
      </option>
      ${this.mappings.map(e=>W`
          <option value="${e.id}" ?selected="${t===String(e.id)}">
            ${e.id}: ${e.name}
          </option>
        `)}
    `;}renderZone(e,t){var a,i,n,s,r,o,l,d,u;if(!this.hass)return W``;const c=Number(null!==(a=e.bucket)&&void 0!==a?a:0),p=c<0?"var(--warning-color)":"var(--success-color)",h=e.state===tr.Automatic?"state-automatic":e.state===tr.Manual?"state-manual":"state-disabled";return W`
      <ha-card>
        <div class="card-header">
          <div class="name">${e.name}</div>
          <span class="zone-state-badge ${h}">
            ${Es(`panels.zones.labels.states.${e.state}`,this.hass.language)}
          </span>
        </div>

        <!-- STATUS -->
        <div class="card-content">
          <div class="zone-status-grid">
            <div class="status-item">
              <span class="status-label"
                >${Es("panels.zones.labels.bucket",this.hass.language)}</span
              >
              <span class="status-value" style="color: ${p}">
                ${c.toFixed(2)} ${Ds(this.config,ht)}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label"
                >${Es("panels.zones.labels.duration",this.hass.language)}</span
              >
              <span class="status-value">
                ${(null!==(i=e.duration)&&void 0!==i?i:0)>0?`${e.duration} s`:"–"}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label"
                >${Es("panels.zones.labels.last_calculated",this.hass.language)}</span
              >
              <span class="status-value">
                ${e.last_calculated?lr(e.last_calculated).format("YYYY-MM-DD HH:mm"):"–"}
              </span>
            </div>
            <div class="status-item">
              <span class="status-label"
                >${Es("panels.zones.labels.data-number-of-data-points",this.hass.language)}</span
              >
              <span class="status-value"
                >${null!==(n=e.number_of_data_points)&&void 0!==n?n:0}</span
              >
            </div>
          </div>
        </div>

        <!-- ACTION BUTTONS -->
        <div class="card-content zone-action-bar">
          ${e.state===tr.Automatic?W`
                <button
                  class="action-btn"
                  @click="${()=>this.handleCalculateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon slot="icon" icon="mdi:calculator"></ha-icon>
                  ${Es("panels.zones.actions.calculate",this.hass.language)}
                </button>
                <button
                  class="action-btn"
                  @click="${()=>this.handleUpdateZone(t)}"
                  ?disabled="${this.isSaving}"
                >
                  <ha-icon slot="icon" icon="mdi:update"></ha-icon>
                  ${Es("panels.zones.actions.update",this.hass.language)}
                </button>
              `:""}
          ${e.linked_entity&&(null!==(s=e.duration)&&void 0!==s?s:0)>0?W`
                <button
                  class="action-btn"
                  raised
                  @click="${()=>{void 0!==e.id&&(this._confirmIrrigate=e.id.toString());}}"
                  ?disabled="${this.isSaving}"
                >
                  ${Es("panels.zones.labels.irrigate_now",this.hass.language)}
                </button>
              `:""}
        </div>

        <!-- SETTINGS EXPANSION -->
        <ha-expansion-panel
          .header="${Es("common.labels.settings",this.hass.language)}"
        >
          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.name",this.hass.language)}</span
            >
            <input
              type="text"
              class="settings-input"
              .value="${e.name}"
              @input="${a=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[ot]:a.target.value}))}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.size",this.hass.language)}
              (${Ds(this.config,lt)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(e.size.toFixed(2))}"
              @input="${a=>{const i=Math.round(100*a.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[lt]:i}));}}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.throughput",this.hass.language)}
              (${Ds(this.config,dt)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(e.throughput.toFixed(2))}"
              @input="${a=>{const i=Math.round(100*a.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[dt]:i}));}}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.drainage_rate",this.hass.language)}
              (${Ds(this.config,bt)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat((null!==(r=e.drainage_rate)&&void 0!==r?r:0).toFixed(2))}"
              @input="${a=>{const i=Math.round(100*a.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[bt]:i}));}}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.state",this.hass.language)}</span
            >
            <select
              class="settings-input"
              .value="${Is(e.state)}"
              @change="${a=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[ut]:a.target.value,[ct]:0}))}"
            >
              <option
                value="${tr.Automatic}"
                ?selected="${e.state===tr.Automatic}"
              >
                ${Es("panels.zones.labels.states.automatic",this.hass.language)}
              </option>
              <option
                value="${tr.Manual}"
                ?selected="${e.state===tr.Manual}"
              >
                ${Es("panels.zones.labels.states.manual",this.hass.language)}
              </option>
              <option
                value="${tr.Disabled}"
                ?selected="${e.state===tr.Disabled}"
              >
                ${Es("panels.zones.labels.states.disabled",this.hass.language)}
              </option>
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("common.labels.module",this.hass.language)}</span
            >
            <select
              class="settings-input"
              .value="${Is(void 0!==e.module?String(e.module):"")}"
              @change="${a=>{const i=a.target.value;this.handleEditZone(t,Object.assign(Object.assign({},e),{[pt]:i?parseInt(i):void 0}));}}"
            >
              ${this._renderModuleOptions(e.module)}
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.mapping",this.hass.language)}</span
            >
            <select
              class="settings-input"
              .value="${Is(void 0!==e.mapping?String(e.mapping):"")}"
              @change="${a=>{const i=a.target.value;this.handleEditZone(t,Object.assign(Object.assign({},e),{[mt]:i?parseInt(i):void 0}));}}"
            >
              ${this._renderMappingOptions(e.mapping)}
            </select>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.linked_entity",this.hass.language)}</span
            >
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${e.linked_entity||""}"
              .includeDomains="${["switch","valve"]}"
              allow-custom-entity
              @value-changed="${a=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[yt]:a.detail.value||void 0}))}"
            ></ha-entity-picker>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.flow_sensor",this.hass.language)}</span
            >
            <ha-entity-picker
              .hass="${this.hass}"
              .value="${e.flow_sensor||""}"
              .includeDomains="${["sensor"]}"
              allow-custom-entity
              @value-changed="${a=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[kt]:a.detail.value||null}))}"
            ></ha-entity-picker>
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.bucket",this.hass.language)}
              (${Ds(this.config,ht)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              inputmode="decimal"
              .value="${parseFloat(Number(e.bucket).toFixed(2))}"
              @input="${a=>{const i=Math.round(100*a.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ht]:i}));}}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.maximum-bucket",this.hass.language)}
              (${Ds(this.config,ht)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(Number(e.maximum_bucket).toFixed(2))}"
              @input="${a=>{const i=Math.round(100*a.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[_t]:i}));}}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.multiplier",this.hass.language)}</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${parseFloat(e.multiplier.toFixed(2))}"
              @input="${a=>{const i=Math.round(100*a.target.valueAsNumber)/100;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[gt]:i}));}}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.lead-time",this.hass.language)}
              (s)</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="1"
              min="0"
              inputmode="numeric"
              .value="${null!==(o=e.lead_time)&&void 0!==o?o:0}"
              @input="${a=>{const i=a.target.valueAsNumber;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[vt]:Math.round(i)}));}}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.maximum-duration",this.hass.language)}
              (s)</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="1"
              min="0"
              inputmode="numeric"
              .value="${null!==(l=e.maximum_duration)&&void 0!==l?l:""}"
              @input="${a=>{const i=a.target.valueAsNumber;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ft]:Math.round(i)}));}}"
            />
          </ha-settings-row>

          <ha-settings-row>
            <span slot="heading"
              >${Es("panels.zones.labels.bucket_threshold",this.hass.language)}
              (${Ds(this.config,ht)})</span
            >
            <input
              type="number"
              class="settings-input shortfield"
              step="0.5"
              max="0"
              inputmode="decimal"
              .value="${parseFloat((null!==(d=e.bucket_threshold)&&void 0!==d?d:0).toFixed(1))}"
              @input="${a=>{const i=Math.round(10*a.target.valueAsNumber)/10;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[wt]:Math.min(i,0)}));}}"
            />
          </ha-settings-row>

          ${e.state===tr.Manual?W`
                <ha-settings-row>
                  <span slot="heading"
                    >${Es("panels.zones.labels.duration",this.hass.language)}
                    (${"s"})</span
                  >
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="1"
                    min="0"
                    inputmode="numeric"
                    .value="${null!==(u=e.duration)&&void 0!==u?u:0}"
                    @input="${a=>{const i=a.target.valueAsNumber;isNaN(i)||this.handleEditZone(t,Object.assign(Object.assign({},e),{[ct]:Math.round(i)}));}}"
                  />
                </ha-settings-row>
              `:""}

          <!-- Danger row -->
          <div class="settings-danger-row">
            <button
              class="action-btn"
              @click="${()=>this.handleEditZone(t,Object.assign(Object.assign({},e),{[ht]:0}))}"
              ?disabled="${this.isSaving}"
            >
              ${Es("panels.zones.actions.reset-bucket",this.hass.language)}
            </button>
            <button
              class="action-btn"
              class="danger-button"
              @click="${()=>this.handleRemoveZone(void 0!==e.id?e.id:-1)}"
              ?disabled="${this.isSaving||void 0===e.id}"
            >
              <ha-icon slot="icon" icon="mdi:delete"></ha-icon>
              ${Es("common.actions.delete",this.hass.language)}
            </button>
          </div>
        </ha-expansion-panel>

        <!-- EXPLANATION EXPANSION -->
        ${e.explanation&&e.explanation.length>0?W`
              <ha-expansion-panel
                .header="${Es("panels.zones.actions.information",this.hass.language)}"
              >
                <div class="card-content">${Nt(e.explanation)}</div>
              </ha-expansion-panel>
            `:""}

        <!-- WEATHER EXPANSION -->
        ${void 0!==e.mapping?W`
              <ha-expansion-panel
                .header="${Es("panels.zones.actions.view-weather-info",this.hass.language)}"
              >
                ${this.renderWeatherRecords(e)}
              </ha-expansion-panel>
            `:""}

        <!-- CALENDAR EXPANSION -->
        <ha-expansion-panel
          .header="${Es("panels.zones.actions.view-watering-calendar",this.hass.language)}"
        >
          ${this.renderWateringCalendar(e)}
        </ha-expansion-panel>
      </ha-card>
    `;}render(){var e,t,a,i;if(!this.hass)return W``;if(this.isLoading)return W`
        <ha-card header="${Es("panels.zones.title",this.hass.language)}">
          <div class="card-content">
            ${Es("common.loading-messages.general",this.hass.language)}...
          </div>
        </ha-card>
      `;const n=null!==this._confirmDeleteZoneId?this.zones.find(e=>e.id===this._confirmDeleteZoneId):null,s=this.zones.some(e=>{var t;return e.linked_entity&&(null!==(t=e.duration)&&void 0!==t?t:0)>0;}),r=0===this.zones.length&&0===this.modules.length&&0===this.mappings.length;return W`
      ${r?W`
            <ha-card class="setup-banner-card">
              <div class="setup-banner">
                <div class="setup-banner-icon">🌱</div>
                <div class="setup-banner-content">
                  <div class="setup-banner-title">
                    ${Es("wizard.title",this.hass.language)}
                  </div>
                  <div class="setup-banner-desc">
                    ${Es("wizard.setup_complete_banner",this.hass.language)}
                  </div>
                </div>
                <button
                  class="action-btn setup-banner-btn"
                  @click="${()=>{this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}));}}"
                >
                  ${Es("wizard.open_wizard",this.hass.language)}
                </button>
              </div>
            </ha-card>
          `:""}
      <!-- Zones header card with + button and Irrigate All -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${Es("panels.zones.title",this.hass.language)}
          </div>
          <ha-icon-button
            .path="${Bs}"
            @click="${()=>{this._showAddZone=!0;}}"
          ></ha-icon-button>
        </div>
        <div class="card-content zones-top-actions">
          <button
            class="action-btn"
            raised
            @click="${()=>{this._confirmIrrigate="all";}}"
            ?disabled="${!s||this.isSaving}"
          >
            ${Es("panels.zones.actions.irrigate_all",this.hass.language)}
          </button>
          ${s?"":W`<span class="zones-top-note"
                >${Es("panels.info.cards.irrigate_now.no_linked_zones",this.hass.language)}</span
              >`}
        </div>
      </ha-card>

      <!-- Add Zone dialog -->
      <ha-dialog
        .open="${this._showAddZone}"
        @closed="${()=>{this._showAddZone=!1;}}"
        heading="${Es("panels.zones.cards.add-zone.header",this.hass.language)}"
      >
        <div class="add-zone-form">
          <si-field
            label="${Es("panels.zones.labels.name",this.hass.language)}"
            required
          >
            <input
              type="text"
              class="settings-input add-zone-input"
              .value="${this._newZoneName}"
              @input="${e=>{this._newZoneName=e.target.value;}}"
            />
          </si-field>
          <si-field
            label="${Es("panels.zones.labels.size",this.hass.language)}"
            unit="${(null===(e=this.config)||void 0===e?void 0:e.units)===Oe?"m²":at}"
            help="${Es("field_help.zone_size",this.hass.language)}"
          >
            <input
              type="number"
              class="settings-input add-zone-input"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${this._newZoneSize}"
              @input="${e=>{this._newZoneSize=e.target.value;}}"
            />
          </si-field>
          <si-field
            label="${Es("panels.zones.labels.throughput",this.hass.language)}"
            unit="${(null===(t=this.config)||void 0===t?void 0:t.units)===Oe?it:nt}"
            help="${Es("field_help.zone_throughput",this.hass.language)}"
          >
            <input
              type="number"
              class="settings-input add-zone-input"
              step="0.1"
              min="0"
              inputmode="decimal"
              .value="${this._newZoneThroughput}"
              @input="${e=>{this._newZoneThroughput=e.target.value;}}"
            />
          </si-field>
        </div>
        <div class="dialog-footer">
          <button
            class="dialog-btn"
            @click="${()=>{this._showAddZone=!1;}}"
          >
            ${Es("common.actions.cancel",this.hass.language)}
          </button>
          <button
            class="dialog-btn dialog-btn-primary"
            @click="${this.handleAddZone}"
            ?disabled="${!this._newZoneName.trim()||this.isSaving}"
          >
            ${this.isSaving?Es("common.saving-messages.adding",this.hass.language):Es("panels.zones.cards.add-zone.actions.add",this.hass.language)}
          </button>
        </div>
      </ha-dialog>

      <!-- Delete confirmation dialog -->
      ${n?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmDeleteZoneId=null;}}"
              heading="${Es("common.actions.confirm_delete",this.hass.language)}"
            >
              <p>
                ${Es("common.actions.confirm_delete_zone",this.hass.language)}
              </p>
              <p><strong>${n.name}</strong></p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmDeleteZoneId=null;}}"
                >
                  ${Es("common.actions.cancel",this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-danger"
                  @click="${this._confirmDelete}"
                >
                  ${Es("common.actions.delete",this.hass.language)}
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Irrigate confirmation dialog -->
      ${null!==this._confirmIrrigate?W`
            <ha-dialog
              open
              @closed="${()=>{this._confirmIrrigate=null;}}"
              heading="${Es("panels.zones.confirm_irrigate.title",this.hass.language)}"
            >
              <p>
                ${Es("panels.zones.confirm_irrigate.body",this.hass.language)}
              </p>
              <p>
                <strong>
                  ${"all"===this._confirmIrrigate?`${Es("panels.zones.confirm_irrigate.all_linked_zones",this.hass.language)} (${this._linkedZoneCount})`:null!==(i=null===(a=this.zones.find(e=>{var t;return(null===(t=e.id)||void 0===t?void 0:t.toString())===this._confirmIrrigate;}))||void 0===a?void 0:a.name)&&void 0!==i?i:this._confirmIrrigate}
                </strong>
              </p>
              <div class="dialog-footer">
                <button
                  class="dialog-btn"
                  @click="${()=>{this._confirmIrrigate=null;}}"
                >
                  ${Es("common.actions.cancel",this.hass.language)}
                </button>
                <button
                  class="dialog-btn dialog-btn-primary"
                  @click="${this._doIrrigate}"
                >
                  ${Es("panels.zones.labels.irrigate_now",this.hass.language)}
                </button>
              </div>
            </ha-dialog>
          `:""}

      <!-- Operation error banner -->
      ${this._operationError?W`
            <ha-card class="error-banner-card">
              <div class="error-banner">
                <span class="error-banner-msg">${this._operationError}</span>
                <button
                  class="error-banner-close"
                  @click="${()=>{this._operationError=null;}}"
                  aria-label="Dismiss"
                >
                  ✕
                </button>
              </div>
            </ha-card>
          `:""}

      <!-- Bulk actions card -->
      <ha-card>
        <div class="card-header">
          <div class="name">
            ${Es("common.labels.bulk_actions",this.hass.language)}
          </div>
        </div>
        <div class="card-content bulk-actions">
          <button
            class="action-btn"
            @click="${this.handleCalculateAllZones}"
            ?disabled="${this.isSaving}"
          >
            ${Es("panels.zones.cards.zone-actions.actions.calculate-all",this.hass.language)}
          </button>
          <button
            class="action-btn"
            @click="${this.handleUpdateAllZones}"
            ?disabled="${this.isSaving}"
          >
            ${Es("panels.zones.cards.zone-actions.actions.update-all",this.hass.language)}
          </button>
          <button
            class="action-btn"
            @click="${this.handleResetAllBuckets}"
            ?disabled="${this.isSaving}"
          >
            ${Es("panels.zones.cards.zone-actions.actions.reset-all-buckets",this.hass.language)}
          </button>
          <button
            class="action-btn"
            @click="${this.handleClearAllWeatherdata}"
            ?disabled="${this.isSaving}"
          >
            ${Es("panels.zones.cards.zone-actions.actions.clear-all-weatherdata",this.hass.language)}
          </button>
        </div>
      </ha-card>

      <!-- Zone cards -->
      ${this.zones.map((e,t)=>this.renderZone(e,t))}
    `;}disconnectedCallback(){super.disconnectedCallback(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null);}static get styles(){return c`
      ${ar}

      ha-settings-row {
        padding: 0 16px;
      }

      ha-expansion-panel {
        border-top: 1px solid var(--divider-color);
      }

      .shortfield {
        width: 120px;
      }

      /* Zone status grid */
      .zone-status-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 8px;
      }

      .status-item {
        display: flex;
        flex-direction: column;
        gap: 2px;
        padding: 8px;
        background: var(--secondary-background-color);
        border-radius: 8px;
      }

      .status-label {
        font-size: 0.75rem;
        color: var(--secondary-text-color);
        text-transform: uppercase;
        letter-spacing: 0.05em;
      }

      .status-value {
        font-size: 1rem;
        font-weight: 500;
        color: var(--primary-text-color);
      }

      /* Action bar */
      .zone-action-bar {
        display: flex;
        flex-wrap: wrap;
        gap: 8px;
        padding-top: 0;
        padding-bottom: 8px;
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

      /* Zones top action bar */
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

      /* Operation error banner */
      .error-banner-card {
        border-left: 4px solid var(--error-color, #f44336);
      }

      .error-banner {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 12px 16px;
      }

      .error-banner-msg {
        flex: 1;
        color: var(--error-color, #f44336);
        font-size: 0.9rem;
        line-height: 1.4;
      }

      .error-banner-close {
        background: none;
        border: none;
        color: var(--secondary-text-color);
        cursor: pointer;
        font-size: 1rem;
        padding: 0 4px;
        flex-shrink: 0;
      }
    `;}};n([he()],ur.prototype,"config",void 0),n([he({type:Array})],ur.prototype,"zones",void 0),n([he({type:Array})],ur.prototype,"modules",void 0),n([he({type:Array})],ur.prototype,"mappings",void 0),n([he({type:Map})],ur.prototype,"wateringCalendars",void 0),n([he({type:Map})],ur.prototype,"weatherRecords",void 0),n([he({type:Boolean})],ur.prototype,"isLoading",void 0),n([he({type:Boolean})],ur.prototype,"isSaving",void 0),n([he({type:Boolean})],ur.prototype,"_showAddZone",void 0),n([ge()],ur.prototype,"_operationError",void 0),n([ge()],ur.prototype,"_confirmIrrigate",void 0),n([he()],ur.prototype,"_confirmDeleteZoneId",void 0),n([he()],ur.prototype,"_newZoneName",void 0),n([he()],ur.prototype,"_newZoneSize",void 0),n([he()],ur.prototype,"_newZoneThroughput",void 0),ur=n([ce("smart-irrigation-view-zones")],ur);let cr=class extends Qs(de){constructor(){super(...arguments),this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._weatherConfig=null,this._weatherService=null,this._useWeatherService=!1,this._newApiKey="",this._weatherSaving=!1,this._testingApi=!1,this._testResult=null,this._testResultTimer=null,this._updateScheduled=!1,this.debouncedSave=(()=>{let e=null;return t=>{e&&clearTimeout(e),e=window.setTimeout(()=>{this.saveData(t),e=null;},500);};})();}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate();}));}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e);}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e);});},{type:Se+"_config_updated"})];}async _fetchData(){var e;if(!this.hass)return;const t=!this._initialLoadDone;t&&(this.isLoading=!0,this._scheduleUpdate());try{const[t,n]=await Promise.all([Us(this.hass),Ks(this.hass)]);this.config=t,this._weatherConfig=n,this._useWeatherService=n.use_weather_service,this._weatherService=null!==(e=n.weather_service)&&void 0!==e?e:Me,this.data=(a=this.config,i=["calctime","autocalcenabled","autoupdateenabled","autoupdateschedule","autoupdatefirsttime","autoupdateinterval","autoclearenabled","cleardatatime","continuousupdates","sensor_debounce","manual_coordinates_enabled","manual_latitude","manual_longitude","manual_elevation","days_between_irrigation"],a?Object.entries(a).filter(([e])=>i.includes(e)).reduce((e,[t,a])=>Object.assign(e,{[t]:a}),{}):{}),this._initialLoadDone=!0;}catch(e){console.error("Error fetching data:",e),Ns(this,this.hass,"common.errors.load_failed",e);}finally{t&&(this.isLoading=!1),this._scheduleUpdate();}var a,i;}firstUpdated(){be().then(()=>this._scheduleUpdate()).catch(e=>{console.error("Failed to load HA form:",e),this._scheduleUpdate();});}render(){var e,t;return this.hass&&this.config&&this.data?this.isLoading?W`<div class="loading-indicator">
        ${Es("common.loading-messages.general",this.hass.language)}
      </div>`:W`
      ${this._renderWeatherServiceCard()} ${this._renderAutoUpdateCard()}
      ${this._renderAutoCalcCard()} ${this._renderAutoClearCard()}
      ${this._renderContinuousUpdatesCard()} ${this._renderWeatherSkipCard()}
      ${this._renderCoordinateCard()} ${this._renderDaysBetweenIrrigationCard()}
      ${this._renderZoneSequencingCard()}
    `:W`<div class="loading-indicator">
        ${Es("common.loading-messages.configuration",null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en")}
      </div>`;}async _saveWeatherConfig(){if(this.hass){this._weatherSaving=!0,this._scheduleUpdate();try{await Js(this.hass,this._useWeatherService,this._useWeatherService?this._weatherService:null,this._newApiKey||null),this._newApiKey="",await this._fetchData();}catch(e){console.error("Failed to save weather config:",e),Ns(this,this.hass,"common.errors.save_failed",e);}finally{this._weatherSaving=!1,this._scheduleUpdate();}}}async _testWeatherConfig(){if(this.hass&&!this._testingApi){this._testingApi=!0,this._testResult=null,this._testResultTimer&&(clearTimeout(this._testResultTimer),this._testResultTimer=null),this._scheduleUpdate();try{const e=await Xs(this.hass,this._weatherService,this._newApiKey||null);this._testResult=e,this._testResultTimer=window.setTimeout(()=>{this._testResult=null,this._testResultTimer=null,this._scheduleUpdate();},12e3);}catch(e){this._testResult={success:!1,error:"unknown"};}finally{this._testingApi=!1,this._scheduleUpdate();}}}_renderWeatherServiceCard(){var e,t,a,i,n;if(!this.hass)return W``;const s=null!==(t=null===(e=this._weatherConfig)||void 0===e?void 0:e.no_api_key_services)&&void 0!==t?t:[Me],r=this._useWeatherService&&this._weatherService&&!s.includes(this._weatherService);return W`
      <ha-card
        header="${Es("weather_service_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Es("weather_service_config.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("weather_service_config.enabled_label",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this._useWeatherService}"
              @change="${e=>{this._useWeatherService=e.target.checked;}}"
            ></ha-switch>
          </div>
          ${this._useWeatherService?W`
                <div class="setting-row">
                  <label>
                    ${Es("weather_service_config.service_label",this.hass.language)}
                  </label>
                  <select
                    class="settings-input"
                    .value="${Is(this._weatherService||Me)}"
                    @change="${e=>{this._weatherService=e.target.value;}}"
                  >
                    <option
                      value="${Me}"
                      ?selected="${(this._weatherService||Me)===Me}"
                    >
                      ${Es("weather_service_config.openmeteo",this.hass.language)}
                    </option>
                    <option
                      value="${$e}"
                      ?selected="${this._weatherService===$e}"
                    >
                      ${Es("weather_service_config.owm",this.hass.language)}
                    </option>
                    <option
                      value="${Ae}"
                      ?selected="${this._weatherService===Ae}"
                    >
                      ${Es("weather_service_config.pw",this.hass.language)}
                    </option>
                  </select>
                </div>
                ${r?W`
                      <si-field
                        label="${Es("weather_service_config.api_key_label",this.hass.language)}"
                        help="${Es("weather_service_config.api_key_help",this.hass.language)}"
                      >
                        <div class="api-key-status">
                          ${(()=>{const e=this._weatherService,t=this._weatherConfig;return(e===$e?null==t?void 0:t.has_owm_api_key:e===Ae&&(null==t?void 0:t.has_pw_api_key))?W`<span class="api-key-badge configured"
                                  >${Es("weather_service_config.api_key_configured",this.hass.language)}</span
                                >`:W`<span class="api-key-badge missing"
                                  >${Es("weather_service_config.api_key_not_configured",this.hass.language)}</span
                                >`;})()}
                        </div>
                        <div class="api-key-row">
                          <input
                            type="password"
                            class="settings-input api-key-input"
                            placeholder="${Es("weather_service_config.api_key_placeholder",this.hass.language)}"
                            .value="${this._newApiKey}"
                            @input="${e=>{this._newApiKey=e.target.value,this._testResult=null;}}"
                          />
                          <button
                            class="action-btn secondary test-btn"
                            type="button"
                            ?disabled="${this._testingApi||!this._newApiKey&&!(this._weatherService===$e?null===(a=this._weatherConfig)||void 0===a?void 0:a.has_owm_api_key:this._weatherService===Ae&&(null===(i=this._weatherConfig)||void 0===i?void 0:i.has_pw_api_key))}"
                            @click="${this._testWeatherConfig}"
                          >
                            ${this._testingApi?Es("weather_service_config.test_button_testing",this.hass.language):Es("weather_service_config.test_button",this.hass.language)}
                          </button>
                        </div>
                        ${null!==this._testResult?W`
                              <div
                                class="test-result ${this._testResult.success?"success":"error"}"
                              >
                                ${this._testResult.success?Es("weather_service_config.test_success",this.hass.language):Es("weather_service_config.test_error_"+(null!==(n=this._testResult.error)&&void 0!==n?n:"unknown"),this.hass.language)}
                              </div>
                            `:""}
                      </si-field>
                    `:W`
                      <div class="description-text" style="padding: 8px 0;">
                        ${Es("weather_service_config.no_api_key_needed",this.hass.language)}
                      </div>
                    `}
              `:""}
          <div style="margin-top: 12px;">
            <button
              class="action-btn"
              raised
              ?disabled="${this._weatherSaving}"
              @click="${this._saveWeatherConfig}"
            >
              ${this._weatherSaving?Es("common.saving-messages.saving",this.hass.language):Es("weather_service_config.save_button",this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>
    `;}_renderAutoUpdateCard(){var e,t;return this.hass&&this.config&&this.data?W`
      <ha-card
        header="${Es("panels.general.cards.automatic-update.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Es("panels.general.cards.automatic-update.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("panels.general.cards.automatic-update.labels.auto-update-enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autoupdateenabled}"
              @change="${e=>this.handleConfigChange({autoupdateenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autoupdateenabled?W`
                <div class="setting-row">
                  <label>
                    ${Es("panels.general.cards.automatic-update.labels.auto-update-interval",this.hass.language)}
                  </label>
                  <div class="inline-row">
                    <input
                      type="number"
                      class="settings-input shortfield"
                      min="1"
                      step="1"
                      inputmode="numeric"
                      .value="${null!==(e=this.data.autoupdateinterval)&&void 0!==e?e:1}"
                      @input="${e=>{const t=parseInt(e.target.value);isNaN(t)||this.handleConfigChange({autoupdateinterval:t});}}"
                    />
                    <select
                      class="settings-input"
                      .value="${Is(this.data.autoupdateschedule||Te)}"
                      @change="${e=>this.handleConfigChange({autoupdateschedule:e.target.value})}"
                    >
                      <option
                        value="${Ee}"
                        ?selected="${(this.data.autoupdateschedule||Te)===Ee}"
                      >
                        ${Es("panels.general.cards.automatic-update.options.minutes",this.hass.language)}
                      </option>
                      <option
                        value="${Te}"
                        ?selected="${(this.data.autoupdateschedule||Te)===Te}"
                      >
                        ${Es("panels.general.cards.automatic-update.options.hours",this.hass.language)}
                      </option>
                      <option
                        value="${De}"
                        ?selected="${this.data.autoupdateschedule===De}"
                      >
                        ${Es("panels.general.cards.automatic-update.options.days",this.hass.language)}
                      </option>
                    </select>
                  </div>
                </div>
                <div class="setting-row">
                  <label>
                    ${Es("panels.general.cards.automatic-update.labels.auto-update-delay",this.hass.language)}
                    (s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="1"
                    inputmode="numeric"
                    .value="${null!==(t=this.config.autoupdatedelay)&&void 0!==t?t:0}"
                    @input="${e=>{const t=parseInt(e.target.value);isNaN(t)||this.handleConfigChange({autoupdatedelay:t});}}"
                  />
                </div>
              `:""}
        </div>
      </ha-card>
    `:W``;}_renderAutoCalcCard(){return this.hass&&this.config&&this.data?W`
      <ha-card
        header="${Es("panels.general.cards.automatic-duration-calculation.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Es("panels.general.cards.automatic-duration-calculation.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("panels.general.cards.automatic-duration-calculation.labels.auto-calc-enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autocalcenabled}"
              @change="${e=>this.handleConfigChange({autocalcenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autocalcenabled?W`
                <div class="setting-row">
                  <label>
                    ${Es("panels.general.cards.automatic-duration-calculation.labels.calc-time",this.hass.language)}
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
    `:W``;}_renderAutoClearCard(){return this.hass&&this.config&&this.data?W`
      <ha-card
        header="${Es("panels.general.cards.automatic-clear.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Es("panels.general.cards.automatic-clear.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("panels.general.cards.automatic-clear.labels.automatic-clear-enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.autoclearenabled}"
              @change="${e=>this.handleConfigChange({autoclearenabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.autoclearenabled?W`
                <div class="setting-row">
                  <label>
                    ${Es("panels.general.cards.automatic-clear.labels.automatic-clear-time",this.hass.language)}
                  </label>
                  <input
                    type="text"
                    class="settings-input shortfield"
                    .value="${this.config.cleardatatime}"
                    @input="${e=>this.handleConfigChange({cleardatatime:e.target.value})}"
                  />
                </div>
              `:""}
        </div>
      </ha-card>
    `:W``;}_renderContinuousUpdatesCard(){var e;return this.hass&&this.config&&this.data?W`
      <ha-card
        header="${Es("panels.general.cards.continuousupdates.header",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Es("panels.general.cards.continuousupdates.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("panels.general.cards.continuousupdates.labels.continuousupdates",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.continuousupdates}"
              @change="${e=>this.handleConfigChange({continuousupdates:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.data.continuousupdates?W`
                <div class="setting-row">
                  <label>
                    ${Es("panels.general.cards.continuousupdates.labels.sensor_debounce",this.hass.language)}
                    (ms)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="1"
                    inputmode="numeric"
                    .value="${null!==(e=this.config.sensor_debounce)&&void 0!==e?e:100}"
                    @input="${e=>{const t=parseInt(e.target.value);isNaN(t)||this.handleConfigChange({sensor_debounce:t});}}"
                  />
                </div>
              `:""}
        </div>
      </ha-card>
    `:W``;}_renderWeatherSkipCard(){var e,t,a;return this.hass&&this.config&&this.data?W`
      <ha-card header="${Es("weather_skip.title",this.hass.language)}">
        <div class="card-content description-text">
          ${Es("weather_skip.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("weather_skip.threshold_label",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_irrigation_on_precipitation}"
              @change="${e=>this.handleConfigChange({skip_irrigation_on_precipitation:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_irrigation_on_precipitation?W`
                <div class="setting-row">
                  <label>
                    ${Es("weather_skip.threshold_label",this.hass.language)}
                    (${Ds(this.config,xe)})
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${null!==(e=this.config.precipitation_threshold_mm)&&void 0!==e?e:2}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({precipitation_threshold_mm:t});}}"
                  />
                </div>
              `:""}

          <div class="section-divider">
            ${Es("weather_skip.temp_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Es("weather_skip.temp_section_title",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_temp_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_temp_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_temp_enabled?W`
                <div class="setting-row">
                  <label>
                    ${Es("weather_skip.temp_threshold_label",this.hass.language)}
                    (°C)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    step="0.5"
                    .value="${null!==(t=this.config.temp_threshold)&&void 0!==t?t:5}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({temp_threshold:t});}}"
                  />
                </div>
              `:""}

          <div class="section-divider">
            ${Es("weather_skip.wind_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Es("weather_skip.wind_section_title",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.skip_on_wind_enabled}"
              @change="${e=>this.handleConfigChange({skip_on_wind_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.skip_on_wind_enabled?W`
                <div class="setting-row">
                  <label>
                    ${Es("weather_skip.wind_threshold_label",this.hass.language)}
                    (m/s)
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="0"
                    step="0.1"
                    inputmode="decimal"
                    .value="${null!==(a=this.config.wind_threshold)&&void 0!==a?a:6.9}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({wind_threshold:t});}}"
                  />
                </div>
              `:""}

          <div class="section-divider">
            ${Es("weather_skip.rain_sensor_section_title",this.hass.language)}
          </div>
          <div class="setting-row">
            <label>
              ${Es("weather_skip.rain_sensor_label",this.hass.language)}
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
    `:W``;}_renderCoordinateCard(){var e,t,a;if(!this.hass||!this.config||!this.data)return W``;const i=this.hass.config,n=(null==i?void 0:i.latitude)||0,s=(null==i?void 0:i.longitude)||0,r=(null==i?void 0:i.elevation)||0;return W`
      <ha-card
        header="${Es("coordinate_config.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Es("coordinate_config.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("coordinate_config.manual_enabled",this.hass.language)}
            </label>
            <ha-switch
              .checked="${this.config.manual_coordinates_enabled}"
              @change="${e=>this.handleConfigChange({manual_coordinates_enabled:e.target.checked})}"
            ></ha-switch>
          </div>
          ${this.config.manual_coordinates_enabled?W`
                <div class="setting-row">
                  <label>
                    ${Es("coordinate_config.latitude",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-90"
                    max="90"
                    step="0.000001"
                    inputmode="decimal"
                    .value="${null!==(e=this.config.manual_latitude)&&void 0!==e?e:n}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({manual_latitude:t});}}"
                  />
                </div>
                <div class="setting-row">
                  <label>
                    ${Es("coordinate_config.longitude",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-180"
                    max="180"
                    step="0.000001"
                    inputmode="decimal"
                    .value="${null!==(t=this.config.manual_longitude)&&void 0!==t?t:s}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({manual_longitude:t});}}"
                  />
                </div>
                <div class="setting-row">
                  <label>
                    ${Es("coordinate_config.elevation",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    class="settings-input shortfield"
                    min="-1000"
                    max="9000"
                    step="1"
                    inputmode="numeric"
                    .value="${null!==(a=this.config.manual_elevation)&&void 0!==a?a:r}"
                    @input="${e=>{const t=parseFloat(e.target.value);isNaN(t)||this.handleConfigChange({manual_elevation:t});}}"
                  />
                </div>
              `:W`
                <div
                  class="card-content"
                  style="color: var(--secondary-text-color); font-style: italic;"
                >
                  ${Es("coordinate_config.current_ha_coords",this.hass.language)}:
                  ${Es("coordinate_config.latitude",this.hass.language)}:
                  ${n},
                  ${Es("coordinate_config.longitude",this.hass.language)}:
                  ${s},
                  ${Es("coordinate_config.elevation",this.hass.language)}:
                  ${r}m
                </div>
              `}
        </div>
      </ha-card>
    `;}_renderDaysBetweenIrrigationCard(){var e;return this.hass&&this.config&&this.data?W`
      <ha-card
        header="${Es("days_between_irrigation.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Es("days_between_irrigation.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("days_between_irrigation.label",this.hass.language)}
              <div class="setting-description">
                ${Es("days_between_irrigation.help_text",this.hass.language)}
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
              @input="${e=>{const t=e.target.valueAsNumber;isNaN(t)||this.handleConfigChange({days_between_irrigation:Math.round(t)});}}"
            />
          </div>
        </div>
      </ha-card>
    `:W``;}_renderZoneSequencingCard(){var e,t;if(!this.hass||!this.config||!this.data)return W``;const a=(this.config.zone_sequencing||xt)===$t;return W`
      <ha-card
        header="${Es("zone_sequencing.title",this.hass.language)}"
      >
        <div class="card-content description-text">
          ${Es("zone_sequencing.description",this.hass.language)}
        </div>
        <div class="card-content">
          <div class="setting-row">
            <label>
              ${Es("zone_sequencing.title",this.hass.language)}
            </label>
            <select
              class="settings-input"
              .value="${Is(this.config.zone_sequencing||xt)}"
              @change="${e=>this.handleConfigChange({[zt]:e.target.value})}"
            >
              <option
                value="${xt}"
                ?selected="${(this.config.zone_sequencing||xt)===xt}"
              >
                ${Es("zone_sequencing.parallel",this.hass.language)}
              </option>
              <option
                value="${St}"
                ?selected="${this.config.zone_sequencing===St}"
              >
                ${Es("zone_sequencing.sequential",this.hass.language)}
              </option>
              <option
                value="${$t}"
                ?selected="${this.config.zone_sequencing===$t}"
              >
                ${Es("zone_sequencing.rotating",this.hass.language)}
              </option>
            </select>
          </div>
          ${a?W`
                <div class="setting-row">
                  <label>
                    ${Es("zone_sequencing.max_consecutive_duration_label",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    min="1"
                    class="settings-input"
                    .value="${Is(null!==(e=this.config.zone_sequencing_max_consecutive_duration)&&void 0!==e?e:5)}"
                    @change="${e=>this.handleConfigChange({[At]:parseInt(e.target.value,10)||5})}"
                  />
                  <span class="unit-label">
                    ${Es("zone_sequencing.max_consecutive_duration_unit",this.hass.language)}
                  </span>
                </div>
                <div class="setting-row">
                  <label>
                    ${Es("zone_sequencing.min_absorption_time_label",this.hass.language)}
                  </label>
                  <input
                    type="number"
                    min="0"
                    class="settings-input"
                    .value="${Is(null!==(t=this.config.zone_sequencing_min_absorption_time)&&void 0!==t?t:0)}"
                    @change="${e=>this.handleConfigChange({[Mt]:parseInt(e.target.value,10)||0})}"
                  />
                  <span class="unit-label">
                    ${Es("zone_sequencing.min_absorption_time_unit",this.hass.language)}
                  </span>
                </div>
              `:""}
        </div>
      </ha-card>
    `;}async saveData(e){if(this.hass&&this.data){this.isSaving=!0,this._scheduleUpdate();try{this.data=Object.assign(Object.assign({},this.data),e),this._scheduleUpdate(),await(t=this.hass,a=this.data,t.callApi("POST",Se+"/config",a));}catch(e){console.error("Error saving config:",e),js(e,this.shadowRoot.querySelector("ha-card")),await this._fetchData();}finally{this.isSaving=!1,this._scheduleUpdate();}var t,a;}}handleConfigChange(e){this.debouncedSave(e);}disconnectedCallback(){super.disconnectedCallback();}static get styles(){return c`
      ${ar}

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
    `;}};n([he()],cr.prototype,"narrow",void 0),n([he()],cr.prototype,"path",void 0),n([he()],cr.prototype,"data",void 0),n([he()],cr.prototype,"config",void 0),n([he({type:Boolean})],cr.prototype,"isLoading",void 0),n([he({type:Boolean})],cr.prototype,"isSaving",void 0),n([he()],cr.prototype,"_weatherConfig",void 0),n([he()],cr.prototype,"_weatherService",void 0),n([he({type:Boolean})],cr.prototype,"_useWeatherService",void 0),n([he()],cr.prototype,"_newApiKey",void 0),n([he({type:Boolean})],cr.prototype,"_weatherSaving",void 0),n([ge()],cr.prototype,"_testingApi",void 0),n([ge()],cr.prototype,"_testResult",void 0),cr=n([ce("smart-irrigation-view-general")],cr);let pr=class extends Qs(de){constructor(){super(...arguments),this.zones=[],this.modules=[],this.allmodules=[],this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this._updateScheduled=!1,this.globalDebounceTimer=null,this.moduleCache=new Map(),this.debouncedSave=(()=>{let e=null;return t=>{e&&clearTimeout(e),e=window.setTimeout(()=>{this.saveToHA(t),e=null;},500);};})();}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate();}));}firstUpdated(){be().catch(e=>{console.error("Failed to load HA form:",e);});}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e);}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e);});},{type:Se+"_config_updated"})];}async _fetchData(){if(!this.hass)return;const e=!this._initialLoadDone;e&&(this.isLoading=!0,this._scheduleUpdate());try{const[e,t,a,i]=await Promise.all([Us(this.hass),Rs(this.hass),Fs(this.hass),qs(this.hass)]);this.config=e,this.zones=t,this.modules=a,this.allmodules=i,this._initialLoadDone=!0,this.moduleCache.clear();}catch(e){console.error("Error fetching data:",e),Ns(this,this.hass,"common.errors.load_failed",e);}finally{e&&(this.isLoading=!1),this._scheduleUpdate();}}async handleAddModule(){var e,t;if((null===(t=null===(e=this.moduleInput)||void 0===e?void 0:e.selectedOptions)||void 0===t?void 0:t[0])&&!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.moduleInput.selectedOptions[0].text,t=this.allmodules.find(t=>t.name===e);if(!t)return;const a={name:e,description:t.description,config:t.config,schema:t.schema};this.modules=[...this.modules,a],this.moduleCache.clear(),this._scheduleUpdate(),await this.saveToHA(a),await this._fetchData();}catch(e){console.error("Error adding module:",e),await this._fetchData();}finally{this.isSaving=!1,this._scheduleUpdate();}}}async handleRemoveModule(e,t){if(!this.isSaving){this.isSaving=!0,this._scheduleUpdate();try{const e=this.modules[t],n=null==e?void 0:e.id;this.modules;this.modules=this.modules.filter((e,a)=>a!==t),this.moduleCache.clear(),this._scheduleUpdate(),this.hass&&void 0!==n&&(await(a=this.hass,i=n.toString(),a.callApi("POST",Se+"/modules",{id:i,remove:!0})));}catch(e){console.error("Error removing module:",e),Ns(this,this.hass,"common.errors.delete_failed",e),await this._fetchData();}finally{this.isSaving=!1,this._scheduleUpdate();}var a,i;}}async saveToHA(e){if(this.hass)try{await Vs(this.hass,e);}catch(e){throw console.error("Error saving module:",e),Ns(this,this.hass,"common.errors.save_failed",e),e;}}renderModule(e,t){if(!this.hass)return W``;const a=`module-${e.id||t}-${JSON.stringify(e)}`;if(this.moduleCache.has(a))return this.moduleCache.get(a);const i=this.zones.filter(t=>t.module===e.id).length,n=W`
      <ha-card header="${e.id}: ${e.name}">
        <div class="card-content">
          <div class="moduledescription${t}">${e.description}</div>
          <div class="moduleconfig">
            <label class="subheader"
              >${Es("panels.modules.cards.module.labels.configuration",this.hass.language)}
              (*
              ${Es("panels.modules.cards.module.labels.required",this.hass.language)})</label
            >
            ${e.schema?Object.entries(e.schema).map(([e])=>this.renderConfig(t,e)):null}
          </div>
          ${i?W`<div class="weather-note">
                ${Es("panels.modules.cards.module.errors.cannot-delete-module-because-zones-use-it",this.hass.language)}
              </div>`:W` <div
                class="action-button"
                @click="${e=>this.handleRemoveModule(e,t)}"
              >
                <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                  <path fill="#404040" d="${Ls}" />
                </svg>
                <span class="action-button-label">
                  ${Es("common.actions.delete",this.hass.language)}
                </span>
              </div>`}
        </div>
      </ha-card>
    `;return this.moduleCache.set(a,n),n;}renderConfig(e,t){const a=Object.values(this.modules).at(e);if(!a||!this.hass)return;const i=a.schema[t],n=i.name,s=function(e){if(e)return(e=e.replace("_"," ")).charAt(0).toUpperCase()+e.slice(1);}(n);let r="";null==a.config&&(a.config=[]),n in a.config&&(r=a.config[n]);let o=W`<label for="${n+e}"
      >${s} </label
    `;if("boolean"==i.type)o=W`${o}<input
          type="checkbox"
          id="${n+e}"
          .checked=${r}
          @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[n]:t.target.checked})}))}"
        />`;else if("float"==i.type||"integer"==i.type)o=W`${o}<input
          type="number"
          class="shortinput"
          id="${i.name+e}"
          .value="${a.config[i.name]}"
          @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[n]:t.target.value})}))}"
        />`;else if("string"==i.type)o=W`${o}<input
          type="text"
          id="${n+e}"
          .value="${r}"
          @input="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[n]:t.target.value})}))}"
        />`;else if("select"==i.type){const t=this.hass.language;o=W`${o}<select
          id="${n+e}"
          .value="${Is(r)}"
          @change="${t=>this.handleEditConfig(e,Object.assign(Object.assign({},a),{config:Object.assign(Object.assign({},a.config),{[n]:t.target.value})}))}"
        >
          ${Object.entries(i.options).map(([e,a])=>W`<option
                value="${Ts(a,0)}"
                ?selected="${r===Ts(a,0)}"
              >
                ${Es("panels.modules.cards.module.translated-options."+Ts(a,1),t)}
              </option>`)}
        </select>`;}i.required&&(o=W`${o}`);const l=i.description?W`<div class="field-hint">${i.description}</div>`:W``;return o=W`<div class="schemaline">${o}${l}</div>`,o;}handleEditConfig(e,t){this.modules=Object.values(this.modules).map((a,i)=>i===e?t:a),this.moduleCache.clear(),this._scheduleUpdate(),this.debouncedSave(t);}renderOption(e,t){return this.hass?W`<option value="${e}>${t}</option>`:W``;}render(){return this.hass?W`
      <ha-card header="${Es("panels.modules.title",this.hass.language)}">
        <div class="card-content">
          ${Es("panels.modules.description",this.hass.language)}
        </div>
      </ha-card>

      <ha-card
        header="${Es("panels.modules.cards.add-module.header",this.hass.language)}"
      >
        <div class="card-content">
          ${this.isLoading?W`<div class="loading-indicator">
                ${Es("common.loading-messages.general",this.hass.language)}
              </div>`:W`
                <div class="zoneline">
                  <label for="moduleInput"
                    >${Es("common.labels.module",this.hass.language)}:</label
                  >
                  <select id="moduleInput" ?disabled="${this.isSaving}">
                    ${Object.entries(this.allmodules).map(([e,t])=>W`<option value="${t.id}">
                          ${t.name}
                        </option>`)}
                  </select>
                </div>
                <div class="zoneline">
                  <span></span>
                  <button
                    @click="${this.handleAddModule}"
                    ?disabled="${this.isSaving}"
                    class="${this.isSaving?"saving":""}"
                  >
                    ${this.isSaving?Es("common.saving-messages.adding",this.hass.language):Es("panels.modules.cards.add-module.actions.add",this.hass.language)}
                  </button>
                </div>
              `}
        </div>
      </ha-card>

      ${this.isLoading?W`<div class="loading-indicator">
            ${Es("common.loading-messages.modules",this.hass.language)}
          </div>`:Object.entries(this.modules).map(([e,t])=>this.renderModule(t,parseInt(e)))}
    `:W``;}disconnectedCallback(){super.disconnectedCallback(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.moduleCache.clear();}static get styles(){return c`
      ${ar}

      .field-hint {
        font-size: 0.8rem;
        color: var(--secondary-text-color);
        line-height: 1.4;
        margin-top: 3px;
        padding-left: 2px;
      }
    `;}};n([he()],pr.prototype,"config",void 0),n([he({type:Array})],pr.prototype,"zones",void 0),n([he({type:Array})],pr.prototype,"modules",void 0),n([he({type:Array})],pr.prototype,"allmodules",void 0),n([he({type:Boolean})],pr.prototype,"isLoading",void 0),n([he({type:Boolean})],pr.prototype,"isSaving",void 0),n([me("#moduleInput")],pr.prototype,"moduleInput",void 0),pr=n([ce("smart-irrigation-view-modules")],pr);let hr=class extends Qs(de){constructor(){super(...arguments),this.zones=[],this.mappings=[],this.weatherRecords=new Map(),this.isLoading=!0,this._initialLoadDone=!1,this.isSaving=!1,this.debounceTimers=new Map(),this.globalDebounceTimer=null,this.mappingCache=new Map(),this._updateScheduled=!1,this._lastUpdateTime=0,this._updateThrottleDelay=16;}_scheduleUpdate(){if(this._updateScheduled)return;const e=performance.now()-this._lastUpdateTime;e<this._updateThrottleDelay?setTimeout(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate();},this._updateThrottleDelay-e):(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this._lastUpdateTime=performance.now(),this.requestUpdate();}));}firstUpdated(){be().catch(e=>{console.error("Failed to load HA form:",e);});}hassSubscribe(){return this._fetchData().catch(e=>{console.error("Failed to fetch initial data:",e);}),[this.hass.connection.subscribeMessage(()=>{this._fetchData().catch(e=>{console.error("Failed to fetch data on config update:",e);});},{type:Se+"_config_updated"})];}async _fetchData(){var e;if(!this.hass)return;const t=!this._initialLoadDone;try{t&&(this.isLoading=!0);const[e,a,i]=await Promise.all([Us(this.hass),Rs(this.hass),Zs(this.hass)]);this.config=e,this.zones=a,this.mappings=i,this._initialLoadDone=!0,this._fetchWeatherRecords(),this.mappingCache.clear();}catch(t){console.error("Error fetching data:",t),js({body:{message:"Failed to load mapping data"},error:"Data fetch error"},null===(e=this.shadowRoot)||void 0===e?void 0:e.querySelector("ha-card"));}finally{t&&(this.isLoading=!1),this._scheduleUpdate();}}async _fetchWeatherRecords(){if(this.hass){for(const e of this.mappings)if(void 0!==e.id)try{const t=await Gs(this.hass,e.id.toString(),0);this.weatherRecords.set(e.id,t);}catch(t){console.error(`Failed to fetch weather records for mapping ${e.id}:`,t),this.weatherRecords.set(e.id,[]);}this._scheduleUpdate();}}renderWeatherRecords(e){if(!this.hass)return W``;const t=void 0!==e.id&&this.weatherRecords.get(e.id)||[];return W`
      <div class="weather-records">
        <h4>
          ${Es("panels.mappings.weather-records.title",this.hass.language)}
        </h4>
        ${0===t.length?W`
              <div class="weather-note">
                ${Es("panels.mappings.weather-records.no-data",this.hass.language)}
              </div>
            `:W`
              <div class="weather-table">
                <div class="weather-header">
                  <span
                    >${Es("panels.mappings.weather-records.timestamp",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.temperature",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.humidity",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.dewpoint",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.wind",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.pressure",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.precipitation",this.hass.language)}</span
                  >
                  <span
                    >${Es("panels.mappings.weather-records.retrieval-time",this.hass.language)}</span
                  >
                </div>
                ${t.map(e=>{const t=e=>{try{const t=lr(e);return t.isValid()?t.format("MM-DD HH:mm"):"-";}catch(e){return"-";}},a=(e,t,a=1)=>null!=e?e.toFixed(a)+t:"-";return W`
                    <div class="weather-row">
                      <span>${t(e.timestamp)}</span>
                      <span>${a(e.temperature,"°C")}</span>
                      <span>${a(e.humidity,"%")}</span>
                      <span>${a(e.dewpoint,"°C")}</span>
                      <span>${a(e.wind_speed,"m/s")}</span>
                      <span>${a(e.pressure,"hPa",0)}</span>
                      <span>${a(e.precipitation,"mm")}</span>
                      <span>${t(e.retrieval_time)}</span>
                    </div>
                  `;})}
              </div>
            `}
      </div>
    `;}handleAddMapping(){if(!this.mappingNameInput.value.trim())return;const e={[Ce]:"",[Pe]:"",[Ne]:"",[He]:"",[Ie]:"",[Le]:"",[Be]:"",[Ue]:"",[Re]:""},t={name:this.mappingNameInput.value.trim(),mappings:e};this.mappings=[...this.mappings,t],this.isSaving=!0,this.saveToHA(t).then(()=>(this.mappingNameInput.value="",this._fetchData())).catch(e=>{console.error("Failed to add mapping:",e),Ns(this,this.hass,"common.errors.save_failed",e),this.mappings=this.mappings.slice(0,-1);}).finally(()=>{this.isSaving=!1,this._scheduleUpdate();});}handleRemoveMapping(e,t){const a=this.mappings[t].id;if(null==a)return;const i=[...this.mappings];var n,s;(this.mappings=this.mappings.filter((e,a)=>a!==t),this.mappingCache.delete(a.toString()),this.hass)&&(this.isSaving=!0,(n=this.hass,s=a.toString(),n.callApi("POST",Se+"/mappings",{id:s,remove:!0})).catch(e=>{console.error("Failed to delete mapping:",e),Ns(this,this.hass,"common.errors.delete_failed",e),this.mappings=i,this._fetchData().catch(e=>{console.error("Failed to refresh data after delete error:",e);});}).finally(()=>{this.isSaving=!1,this._scheduleUpdate();}));}handleEditMapping(e,t){this.mappings[e]=t,t.id&&this.mappingCache.delete(t.id.toString()),this.globalDebounceTimer&&clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=window.setTimeout(()=>{this.isSaving=!0,this.saveToHA(t).catch(e=>{console.error("Failed to save mapping:",e),Ns(this,this.hass,"common.errors.save_failed",e);}).finally(()=>{this.isSaving=!1,this._scheduleUpdate();}),this.globalDebounceTimer=null;},500),this._scheduleUpdate();}async saveToHA(e){var t;if(!this.hass)throw new Error("Home Assistant connection not available");const a=[],i=this.hass.states;for(const t in e.mappings){const n=e.mappings[t].sensorentity;if(n&&""!==n.trim()){const s=n.trim();e.mappings[t].sensorentity=s,s in i||a.push(s);}}if(a.length>0){const e=null===(t=this.shadowRoot)||void 0===t?void 0:t.querySelector("ha-card");throw e&&js({body:{message:Es("panels.mappings.cards.mapping.errors.source_does_not_exist",this.hass.language)+": "+a.join(", ")},error:Es("panels.mappings.cards.mapping.errors.invalid_source",this.hass.language)},e),new Error("Invalid sensor entities found");}const{id:n,name:s,mappings:r}=e;await Ys(this.hass,{id:n,name:s,mappings:r});}renderMapping(e,t){if(!this.hass)return W``;const a=`${e.id}_${JSON.stringify(e).slice(0,100)}`;if(this.mappingCache.has(a))return this.mappingCache.get(a);const i=this.zones.filter(t=>t.mapping===e.id).length,n=W`
      <ha-card header="${e.id}: ${e.name}">
        <div class="card-content">
          <div class="card-content">
            <label for="name${e.id}"
              >${Es("panels.mappings.labels.mapping-name",this.hass.language)}:</label
            >
            <input
              id="name${e.id}"
              type="text"
              .value="${e.name}"
              @input="${a=>this.handleEditMapping(t,Object.assign(Object.assign({},e),{name:a.target.value}))}"
            />
            ${Object.entries(e.mappings).map(([e])=>this.renderMappingSetting(t,e))}
            ${i?W`<div class="weather-note">
                  ${Es("panels.mappings.cards.mapping.errors.cannot-delete-mapping-because-zones-use-it",this.hass.language)}
                </div>`:W` <div
                  class="action-button"
                  @click="${e=>this.handleRemoveMapping(e,t)}"
                >
                  <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                    <path fill="#404040" d="${Ls}" />
                  </svg>
                  <span class="action-button-label">
                    ${Es("common.actions.delete",this.hass.language)}
                  </span>
                </div>`}
          </div>
        </div>
      </ha-card>
    `;return this.mappingCache.set(a,n),n;}renderMappingSetting(e,t){const a=this.mappings[e];if(!a||!this.hass)return W``;const i=a.mappings[t];return W`
      <div class="mappingline">
        <div class="mappingsettingname">
          <label for="${`${t}_${e}`}">
            ${Es(`panels.mappings.cards.mapping.items.${t.toLowerCase()}`,this.hass.language)}
          </label>
        </div>
        <div class="mappingsettingline">
          <label
            >${Es("panels.mappings.cards.mapping.source",this.hass.language)}:</label
          >
          <div class="radio-group">
            ${this.renderSimpleRadioOptions(e,t,i)}
          </div>
        </div>
        ${this.renderMappingInputs(e,t,i)}
      </div>
    `;}renderSimpleRadioOptions(e,t,a){if(!this.hass||!this.config)return W``;const i=t===Pe||t===Be,n=a[Ke];return W`
      ${!i&&this.config.use_weather_service?W`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${We}"
                ?checked="${n===We}"
                @change="${a=>this.handleSimpleSourceChange(e,t,a)}"
              />
              ${Es("panels.mappings.cards.mapping.sources.weather_service",this.hass.language)}
            </label>
          `:""}
      ${i?W`
            <label>
              <input
                type="radio"
                name="${t}_${e}_source"
                value="${Ge}"
                ?checked="${n===Ge}"
                @change="${a=>this.handleSimpleSourceChange(e,t,a)}"
              />
              ${Es("panels.mappings.cards.mapping.sources.none",this.hass.language)}
            </label>
          `:""}

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${Fe}"
          ?checked="${n===Fe}"
          @change="${a=>this.handleSimpleSourceChange(e,t,a)}"
        />
        ${Es("panels.mappings.cards.mapping.sources.sensor",this.hass.language)}
      </label>

      <label>
        <input
          type="radio"
          name="${t}_${e}_source"
          value="${qe}"
          ?checked="${n===qe}"
          @change="${a=>this.handleSimpleSourceChange(e,t,a)}"
        />
        ${Es("panels.mappings.cards.mapping.sources.static",this.hass.language)}
      </label>
    `;}handleSimpleSourceChange(e,t,a){const i=this.mappings[e],n=a.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Ke]:n,[Xe]:""})})}));}handleSimpleInputChange(e,t,a,i){const n=this.mappings[e],s=i.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},n),{mappings:Object.assign(Object.assign({},n.mappings),{[t]:Object.assign(Object.assign({},n.mappings[t]),{[a]:s})})}));}renderSourceOptions(e,t,a){if(!this.hass)return W``;const i=t===Pe||t===Be;return W`
      <div class="mappingsettingline">
        <label for="${`${t}_${e}`}_source">
          ${Es("panels.mappings.cards.mapping.source",this.hass.language)}:
        </label>
      </div>
      <div class="radio-group">
        ${i?"":this.renderWeatherServiceOption(e,t,a)}
        ${i?this.renderNoneOption(e,t,a):""}
        ${this.renderSensorOption(e,t,a)}
        ${this.renderStaticValueOption(e,t,a)}
      </div>
    `;}renderWeatherServiceOption(e,t,a){if(!this.hass||!this.config)return W``;const i=`${t}_${e}`,n=!this.config.use_weather_service,s=this.config.use_weather_service&&a[Ke]===We;return W`
      <label class="${n?"strikethrough":""}">
        <input
          type="radio"
          id="${i}_weather"
          value="${We}"
          name="${i}_source"
          ?checked="${s}"
          ?disabled="${n}"
          @change="${a=>this.handleSourceChange(e,t,a)}"
        />
        ${Es("panels.mappings.cards.mapping.sources.weather_service",this.hass.language)}
      </label>
    `;}renderNoneOption(e,t,a){if(!this.hass)return W``;const i=`${t}_${e}`,n=a[Ke]===Ge;return W`
      <label>
        <input
          type="radio"
          id="${i}_none"
          value="${Ge}"
          name="${i}_source"
          ?checked="${n}"
          @change="${a=>this.handleSourceChange(e,t,a)}"
        />
        ${Es("panels.mappings.cards.mapping.sources.none",this.hass.language)}
      </label>
    `;}renderSensorOption(e,t,a){if(!this.hass)return W``;const i=`${t}_${e}`,n=a[Ke]===Fe;return W`
      <label>
        <input
          type="radio"
          id="${i}_sensor"
          value="${Fe}"
          name="${i}_source"
          ?checked="${n}"
          @change="${a=>this.handleSourceChange(e,t,a)}"
        />
        ${Es("panels.mappings.cards.mapping.sources.sensor",this.hass.language)}
      </label>
    `;}renderStaticValueOption(e,t,a){if(!this.hass)return W``;const i=`${t}_${e}`,n=a[Ke]===qe;return W`
      <label>
        <input
          type="radio"
          id="${i}_static"
          value="${qe}"
          name="${i}_source"
          ?checked="${n}"
          @change="${a=>this.handleSourceChange(e,t,a)}"
        />
        ${Es("panels.mappings.cards.mapping.sources.static",this.hass.language)}
      </label>
    `;}handleSourceChange(e,t,a){const i=this.mappings[e],n=a.target.value;this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Ke]:n,[Xe]:""})})}));}renderMappingInputs(e,t,a){if(!this.hass)return W``;const i=a[Ke];return W`
      ${i===Fe?this.renderSensorInput(e,t,a):""}
      ${i===qe?this.renderStaticValueInput(e,t,a):""}
      ${i===Fe||i===qe?this.renderUnitSelect(e,t,a):""}
      ${t!==Le||i!==Fe&&i!==qe?"":this.renderPressureTypeSelect(e,t,a)}
      ${i===Fe?this.renderAggregateSelect(e,t,a):""}
    `;}renderSensorInput(e,t,a){if(!this.hass)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_sensor_entity">
          ${Es("panels.mappings.cards.mapping.sensor-entity",this.hass.language)}:
        </label>
        <input
          type="text"
          id="${i}_sensor_entity"
          .value="${a[Xe]||""}"
          @change="${a=>this.handleSensorChange(e,t,a)}"
        />
      </div>
    `;}renderStaticValueInput(e,t,a){if(!this.hass)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_static_value">
          ${Es("panels.mappings.cards.mapping.static_value",this.hass.language)}:
        </label>
        <input
          type="text"
          id="${i}_static_value"
          .value="${a[Je]||""}"
          @input="${a=>this.handleStaticValueChange(e,t,a)}"
        />
      </div>
    `;}renderUnitSelect(e,t,a){if(!this.hass||!this.config)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_unit">
          ${Es("panels.mappings.cards.mapping.input-units",this.hass.language)}:
        </label>
        <select
          id="${i}_unit"
          @change="${a=>this.handleUnitChange(e,t,a)}"
        >
          ${this.renderUnitOptionsForMapping(t,a)}
        </select>
      </div>
    `;}renderPressureTypeSelect(e,t,a){if(!this.hass)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_pressure_type">
          ${Es("panels.mappings.cards.mapping.pressure-type",this.hass.language)}:
        </label>
        <select
          id="${i}_pressure_type"
          @change="${a=>this.handlePressureTypeChange(e,t,a)}"
        >
          ${this.renderPressureTypes(t,a)}
        </select>
      </div>
    `;}renderAggregateSelect(e,t,a){if(!this.hass)return W``;const i=`${t}_${e}`;return W`
      <div class="mappingsettingline">
        <label for="${i}_aggregate">
          ${Es("panels.mappings.cards.mapping.sensor-aggregate-use-the",this.hass.language)}
        </label>
        <select
          id="${i}_aggregate"
          @change="${a=>this.handleAggregateChange(e,t,a)}"
        >
          ${this.renderAggregateOptionsForMapping(t,a)}
        </select>
        <label for="${i}_aggregate">
          ${Es("panels.mappings.cards.mapping.sensor-aggregate-of-sensor-values-to-calculate",this.hass.language)}
        </label>
      </div>
    `;}handleSensorChange(e,t,a){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Xe]:a.target.value})})}));}handleStaticValueChange(e,t,a){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Je]:a.target.value})})}));}handleUnitChange(e,t,a){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Qe]:a.target.value})})}));}handlePressureTypeChange(e,t,a){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[Ve]:a.target.value})})}));}handleAggregateChange(e,t,a){const i=this.mappings[e];this.handleEditMapping(e,Object.assign(Object.assign({},i),{mappings:Object.assign(Object.assign({},i.mappings),{[t]:Object.assign(Object.assign({},i.mappings[t]),{[et]:a.target.value})})}));}renderAggregateOptionsForMapping(e,t){if(!this.hass||!this.config)return W``;let a="average";return e===He&&(a="delta"),e===Ie&&(a="average"),t[et]&&(a=t[et]),W`
      ${tt.map(e=>this.renderAggregateOption(e,a))}
    `;}renderAggregateOption(e,t){if(this.hass&&this.config){return W`<option value="${e}" ?selected="${e===t}">
        ${Es("panels.mappings.cards.mapping.aggregates."+e,this.hass.language)}
      </option>`;}return W``;}renderPressureTypes(e,t){if(this.hass&&this.config){let e=W``;const a=t[Ve];return e=W`${e}
        <option
          value="${Ze}"
          ?selected="${a===Ze}"
        >
          ${Es("panels.mappings.cards.mapping.pressure_types."+Ze,this.hass.language)}
        </option>
        <option
          value="${Ye}"
          ?selected="${a===Ye}"
        >
          ${Es("panels.mappings.cards.mapping.pressure_types."+Ye,this.hass.language)}
        </option>`,e;}return W``;}renderUnitOptionsForMapping(e,t){if(!this.hass||!this.config)return W``;const a=function(e){switch(e){case Ce:case Ue:return[{unit:"°C",system:Oe},{unit:"°F",system:je}];case He:case Pe:return[{unit:"mm",system:Oe},{unit:"in",system:je}];case Ie:return[{unit:st,system:Oe},{unit:rt,system:je}];case Ne:return[{unit:"%",system:[Oe,je]}];case Le:return[{unit:"millibar",system:Oe},{unit:"hPa",system:Oe},{unit:"psi",system:je},{unit:"inch Hg",system:je}];case Re:return[{unit:"km/h",system:Oe},{unit:"meter/s",system:Oe},{unit:"mile/h",system:je}];case Be:return[{unit:"W/m2",system:Oe},{unit:"MJ/day/m2",system:Oe},{unit:"W/sq ft",system:je},{unit:"MJ/day/sq ft",system:je}];default:return[];}}(e);let i=t[Qe];const n=this.config.units;if(!t[Qe])for(const e of a)if("string"==typeof e.system){if(n===e.system){i=e.unit;break;}}else{for(const t of e.system)if(n===t.system){i=e.unit;break;}if(i===e.unit)break;}return W`
      ${a.map(e=>W`
          <option value="${e.unit}" ?selected="${i===e.unit}">
            ${e.unit}
          </option>
        `)}
    `;}render(){return this.hass?this.isLoading?W`
        <ha-card
          header="${Es("panels.mappings.title",this.hass.language)}"
        >
          <div class="card-content">
            ${Es("common.loading-messages.general",this.hass.language)}
          </div>
        </ha-card>
      `:W`
      <ha-card
        header="${Es("panels.mappings.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Es("panels.mappings.description",this.hass.language)}
        </div>
      </ha-card>

      <ha-card
        header="${Es("panels.mappings.cards.add-mapping.header",this.hass.language)}"
      >
        <div class="card-content">
          <div class="zoneline">
            <label for="mappingNameInput"
              >${Es("panels.mappings.labels.mapping-name",this.hass.language)}:</label
            >
            <input id="mappingNameInput" type="text" />
          </div>
          <div class="zoneline">
            <span></span>
            <button @click="${this.handleAddMapping}">
              ${Es("panels.mappings.cards.add-mapping.actions.add",this.hass.language)}
            </button>
          </div>
        </div>
      </ha-card>

      ${this.renderMappingsList()}
    `:W``;}renderMappingsList(){const e=this.mappings.slice(0,Math.min(this.mappings.length,10)),t=this.mappings.slice(10);return W`
      ${e.map((e,t)=>this.renderMappingCard(e,t))}
      ${t.length>0?W`
            <div class="load-more">
              <button @click="${this.loadMoreMappings}">
                Load ${t.length} more mappings...
              </button>
            </div>
          `:""}
    `;}renderMappingCard(e,t){if(!this.hass)return W``;const a=this.zones.filter(t=>t.mapping===e.id).length;return W`
      <ha-card header="${e.id}: ${e.name}">
        <div class="card-content">
          <div class="card-content">
            <label for="name${e.id}"
              >${Es("panels.mappings.labels.mapping-name",this.hass.language)}:</label
            >
            <input
              id="name${e.id}"
              type="text"
              .value="${e.name}"
              @input="${a=>this.handleEditMapping(t,Object.assign(Object.assign({},e),{name:a.target.value}))}"
            />
            ${this.renderMappingSettings(e,t)}
            ${this.renderWeatherRecords(e)}
            ${a?W`<div class="weather-note">
                  ${Es("panels.mappings.cards.mapping.errors.cannot-delete-mapping-because-zones-use-it",this.hass.language)}
                </div>`:W` <div
                  class="action-button"
                  @click="${e=>this.handleRemoveMapping(e,t)}"
                >
                  <svg style="width:24px;height:24px" viewBox="0 0 24 24">
                    <path fill="#404040" d="${Ls}" />
                  </svg>
                  <span class="action-button-label">
                    ${Es("common.actions.delete",this.hass.language)}
                  </span>
                </div>`}
          </div>
        </div>
      </ha-card>
    `;}renderMappingSettings(e,t){const a=Object.entries(e.mappings);return W`
      ${a.map(([e])=>this.renderMappingSetting(t,e))}
    `;}loadMoreMappings(){this._scheduleUpdate();}static get styles(){return c`
      ${ar}/* View-specific styles only - most common styles are now in globalStyle */
    `;}disconnectedCallback(){super.disconnectedCallback(),this.debounceTimers.forEach(e=>{clearTimeout(e);}),this.debounceTimers.clear(),this.globalDebounceTimer&&(clearTimeout(this.globalDebounceTimer),this.globalDebounceTimer=null),this.mappingCache.clear();}};n([he()],hr.prototype,"config",void 0),n([he({type:Array})],hr.prototype,"zones",void 0),n([he({type:Array})],hr.prototype,"mappings",void 0),n([he({type:Map})],hr.prototype,"weatherRecords",void 0),n([he({type:Boolean})],hr.prototype,"isLoading",void 0),n([he({type:Boolean})],hr.prototype,"isSaving",void 0),n([me("#mappingNameInput")],hr.prototype,"mappingNameInput",void 0),hr=n([ce("smart-irrigation-view-mappings")],hr);const gr=["monday","tuesday","wednesday","thursday","friday","saturday","sunday"];let mr=class extends Qs(de){constructor(){super(...arguments),this._schedules=[],this._zones=[],this._isLoading=!0,this._showDialog=!1,this._editingSchedule={name:"",type:"daily",enabled:!0,time:"06:00",action:"irrigate",zones:"all"},this._editingId=null;}hassSubscribe(){return this._load(),[this.hass.connection.subscribeMessage(()=>this._load(),{type:Se+"_config_updated"})];}async _load(){var e;if(this.hass)try{const[t,a]=await Promise.all([(e=this.hass,e.callWS({type:Se+"/schedules"})),Rs(this.hass)]);this._schedules=t||[],this._zones=a||[];}catch(e){console.error("Failed to load schedules",e),Ns(this,this.hass,"common.errors.load_failed",e);}finally{this._isLoading=!1;}}_openAdd(){this._editingSchedule={name:"",type:"daily",enabled:!0,time:"06:00",action:"irrigate",zones:"all"},this._editingId=null,this._showDialog=!0;}_openEdit(e){var t;this._editingSchedule=Object.assign({},e),this._editingId=null!==(t=e.id)&&void 0!==t?t:null,this._showDialog=!0;}_closeDialog(){this._showDialog=!1;}async _save(){const e=Object.assign({},this._editingSchedule);this._editingId&&(e.id=this._editingId);try{await((e,t)=>e.callWS({type:Se+"/schedule_save",schedule:t}))(this.hass,e),this._closeDialog(),await this._load();}catch(e){console.error("Failed to save schedule",e),Ns(this,this.hass,"common.errors.save_failed",e);}}async _delete(e){try{await(t=this.hass,a=e,t.callWS({type:Se+"/schedule_delete",schedule_id:a})),await this._load();}catch(e){console.error("Failed to delete schedule",e),Ns(this,this.hass,"common.errors.delete_failed",e);}var t,a;}_update(e){this._editingSchedule=Object.assign(Object.assign({},this._editingSchedule),e);}_typeLabel(e){return Es(`panels.schedules.types.${e}`,this.hass.language)||e;}_actionLabel(e){return Es(`panels.schedules.actions.${e}`,this.hass.language)||e;}_zonesLabel(e){if("all"===e)return Es("panels.schedules.zones_all",this.hass.language);if(Array.isArray(e)){const t=e.map(e=>{const t=this._zones.find(t=>String(t.id)===String(e));return t?t.name:e;}).join(", ");return t||e.join(", ");}return String(e);}_renderZonePicker(){const e="all"===this._editingSchedule.zones||!Array.isArray(this._editingSchedule.zones),t=e?[]:this._editingSchedule.zones.map(String);return W`
      <div class="field">
        <label
          >${Es("panels.schedules.fields.zones",this.hass.language)}</label
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
            >${Es("panels.schedules.zones_all",this.hass.language)}</label
          >
          <input
            type="radio"
            id="zones_specific"
            name="zones_mode"
            ?checked="${!e}"
            @change=${()=>this._update({zones:[]})}
          />
          <label for="zones_specific"
            >${Es("panels.schedules.zones_specific",this.hass.language)}</label
          >
        </div>
        ${e?"":W`
              <div class="zone-checkboxes">
                ${this._zones.map(e=>W`
                    <label class="zone-check">
                      <input
                        type="checkbox"
                        ?checked="${t.includes(String(e.id))}"
                        @change=${t=>{const a=t.target.checked,i=String(e.id),n=Array.isArray(this._editingSchedule.zones)?[...this._editingSchedule.zones]:[],s=a?[...n,i]:n.filter(e=>e!==i);this._update({zones:s});}}
                      />
                      ${e.name}
                    </label>
                  `)}
              </div>
            `}
      </div>
    `;}_renderTypeFields(){var e;const t=this._editingSchedule;switch(t.type){case"daily":return W`
          <div class="field">
            <label
              >${Es("panels.schedules.fields.time",this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time||"06:00"}"
              @change=${e=>this._update({time:e.target.value})}
            />
          </div>
        `;case"weekly":return W`
          <div class="field">
            <label
              >${Es("panels.schedules.fields.time",this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time||"06:00"}"
              @change=${e=>this._update({time:e.target.value})}
            />
          </div>
          <div class="field">
            <label
              >${Es("panels.schedules.fields.days_of_week",this.hass.language)}</label
            >
            <div class="day-checkboxes">
              ${gr.map(e=>W`
                  <label class="day-check">
                    <input
                      type="checkbox"
                      ?checked="${(t.days_of_week||[]).includes(e)}"
                      @change=${a=>{const i=a.target.checked,n=t.days_of_week||[],s=i?[...n,e]:n.filter(t=>t!==e);this._update({days_of_week:s});}}
                    />
                    ${Es(`panels.schedules.days.${e}`,this.hass.language)}
                  </label>
                `)}
            </div>
          </div>
        `;case"monthly":return W`
          <div class="field">
            <label
              >${Es("panels.schedules.fields.time",this.hass.language)}</label
            >
            <input
              type="time"
              .value="${t.time||"06:00"}"
              @change=${e=>this._update({time:e.target.value})}
            />
          </div>
          <div class="field">
            <label
              >${Es("panels.schedules.fields.day_of_month",this.hass.language)}</label
            >
            <input
              type="number"
              min="1"
              max="31"
              .value="${String(t.day_of_month||1)}"
              @input=${e=>this._update({day_of_month:parseInt(e.target.value)})}
            />
          </div>
        `;case"interval":return W`
          <div class="field">
            <label
              >${Es("panels.schedules.fields.interval_hours",this.hass.language)}</label
            >
            <div class="input-suffix-row">
              <input
                type="number"
                min="1"
                .value="${String(t.interval_hours||24)}"
                @input=${e=>this._update({interval_hours:parseInt(e.target.value)})}
              />
              <span class="suffix"
                >${Es("panels.schedules.hours",this.hass.language)}</span
              >
            </div>
          </div>
        `;case"sunrise":case"sunset":return W`${this._renderSunOffsetFields()}`;case"solar_azimuth":return W`
          <div class="field">
            <label
              >${Es("panels.schedules.fields.azimuth_angle",this.hass.language)}</label
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
        `;default:return W``;}}_renderSunOffsetFields(){var e;const t=this._editingSchedule;return W`
      <div class="field">
        <label
          >${Es("panels.schedules.fields.offset_minutes",this.hass.language)}</label
        >
        <div class="input-suffix-row">
          <input
            type="number"
            step="1"
            .value="${String(null!==(e=t.offset_minutes)&&void 0!==e?e:0)}"
            @input=${e=>this._update({offset_minutes:parseInt(e.target.value)})}
          />
          <span class="suffix"
            >${Es("panels.schedules.minutes",this.hass.language)}</span
          >
        </div>
      </div>
      <div class="field-row">
        <label
          >${Es("panels.schedules.fields.account_for_duration",this.hass.language)}</label
        >
        <input
          type="checkbox"
          ?checked="${!1!==t.account_for_duration}"
          @change=${e=>this._update({account_for_duration:e.target.checked})}
        />
      </div>
    `;}_renderDialog(){if(!this._showDialog)return W``;const e=this._editingSchedule,t=this._editingId?Es("panels.schedules.dialog.edit_title",this.hass.language):Es("panels.schedules.dialog.add_title",this.hass.language);return W`
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
              >${Es("panels.schedules.fields.name",this.hass.language)}</label
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
              >${Es("panels.schedules.fields.type",this.hass.language)}</label
            >
            <select
              @change=${e=>this._update({type:e.target.value})}
            >
              ${["daily","weekly","monthly","interval","sunrise","sunset","solar_azimuth"].map(t=>W`
                  <option value="${t}" ?selected="${e.type===t}">
                    ${this._typeLabel(t)}
                  </option>
                `)}
            </select>
          </div>

          ${this._renderTypeFields()}

          <div class="field">
            <label
              >${Es("panels.schedules.fields.action",this.hass.language)}</label
            >
            <select
              @change=${e=>this._update({action:e.target.value})}
            >
              ${["calculate","update","irrigate"].map(t=>W`
                  <option value="${t}" ?selected="${e.action===t}">
                    ${this._actionLabel(t)}
                  </option>
                `)}
            </select>
          </div>

          ${this._renderZonePicker()}

          <div class="field-row">
            <label
              >${Es("panels.schedules.fields.enabled",this.hass.language)}</label
            >
            <input
              type="checkbox"
              ?checked="${e.enabled}"
              @change=${e=>this._update({enabled:e.target.checked})}
            />
          </div>

          <div class="field">
            <label
              >${Es("panels.schedules.fields.start_date",this.hass.language)}</label
            >
            <input
              type="date"
              .value="${e.start_date||""}"
              @change=${e=>this._update({start_date:e.target.value||void 0})}
            />
          </div>

          <div class="field">
            <label
              >${Es("panels.schedules.fields.end_date",this.hass.language)}</label
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
            ${Es("common.actions.cancel",this.hass.language)}
          </button>
          <button class="dialog-btn dialog-btn-primary" @click=${this._save}>
            ${Es("common.actions.save",this.hass.language)}
          </button>
        </div>
      </ha-dialog>
    `;}render(){return this.hass?this._isLoading?W`
        <ha-card
          header="${Es("panels.schedules.title",this.hass.language)}"
        >
          <div class="card-content">
            ${Es("common.loading",this.hass.language)}...
          </div>
        </ha-card>
      `:W`
      ${this._renderDialog()}

      <ha-card
        header="${Es("panels.schedules.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Es("panels.schedules.description",this.hass.language)}
        </div>
        <div class="card-content">
          <button class="add-btn" @click=${this._openAdd}>
            <svg style="width:20px;height:20px" viewBox="0 0 24 24">
              <path fill="currentColor" d="${Bs}" />
            </svg>
            ${Es("panels.schedules.add",this.hass.language)}
          </button>
        </div>
      </ha-card>

      ${0===this._schedules.length?W`
            <ha-card>
              <div class="card-content">
                ${Es("panels.schedules.no_items",this.hass.language)}
              </div>
            </ha-card>
          `:this._schedules.map(e=>W`
              <ha-card header="${e.name}">
                <div class="card-content">
                  <div class="info-row">
                    <span class="info-label"
                      >${Es("panels.schedules.fields.type",this.hass.language)}:</span
                    >
                    <span>${this._typeLabel(e.type)}</span>
                  </div>
                  ${e.time&&["daily","weekly","monthly"].includes(e.type)?W`
                        <div class="info-row">
                          <span class="info-label"
                            >${Es("panels.schedules.fields.time",this.hass.language)}:</span
                          >
                          <span>${e.time}</span>
                        </div>
                      `:""}
                  ${e.interval_hours?W`
                        <div class="info-row">
                          <span class="info-label"
                            >${Es("panels.schedules.fields.interval_hours",this.hass.language)}:</span
                          >
                          <span
                            >${e.interval_hours}
                            ${Es("panels.schedules.hours",this.hass.language)}</span
                          >
                        </div>
                      `:""}
                  <div class="info-row">
                    <span class="info-label"
                      >${Es("panels.schedules.fields.action",this.hass.language)}:</span
                    >
                    <span>${this._actionLabel(e.action)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${Es("panels.schedules.fields.zones",this.hass.language)}:</span
                    >
                    <span>${this._zonesLabel(e.zones)}</span>
                  </div>
                  <div class="info-row">
                    <span class="info-label"
                      >${Es("panels.schedules.fields.enabled",this.hass.language)}:</span
                    >
                    <span
                      >${e.enabled?Es("common.labels.yes",this.hass.language):Es("common.labels.no",this.hass.language)}</span
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
                        >${Es("common.actions.edit",this.hass.language)}</span
                      >
                    </div>
                  </div>
                  <div class="action-buttons-right">
                    <div
                      class="action-button-right"
                      @click=${()=>e.id&&this._delete(e.id)}
                    >
                      <span class="action-button-label"
                        >${Es("common.actions.delete",this.hass.language)}</span
                      >
                      <svg style="width:20px;height:20px" viewBox="0 0 24 24">
                        <path fill="#404040" d="${Ls}" />
                      </svg>
                    </div>
                  </div>
                </div>
              </ha-card>
            `)}
    `:W``;}static get styles(){return[ar,c`
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
      `];}};n([he({attribute:!1})],mr.prototype,"hass",void 0),n([ge()],mr.prototype,"_schedules",void 0),n([ge()],mr.prototype,"_zones",void 0),n([ge()],mr.prototype,"_isLoading",void 0),n([ge()],mr.prototype,"_showDialog",void 0),n([ge()],mr.prototype,"_editingSchedule",void 0),n([ge()],mr.prototype,"_editingId",void 0),mr=n([ce("smart-irrigation-view-schedules")],mr);const vr=()=>{const e=e=>{let t={};for(let a=0;a<e.length;a+=2){const i=e[a],n=a<e.length?e[a+1]:void 0;t=Object.assign(Object.assign({},t),{[i]:n});}return t;},t=window.location.pathname.split("/");let a={page:t[2]||"general",params:{}};if(t.length>3){let i=t.slice(3);if(t.includes("filter")){const t=i.findIndex(e=>"filter"==e),n=i.slice(t+1);i=i.slice(0,t),a=Object.assign(Object.assign({},a),{filter:e(n)});}i.length&&(i.length%2&&(a=Object.assign(Object.assign({},a),{subpage:i.shift()})),i.length&&(a=Object.assign(Object.assign({},a),{params:e(i)})));}return a;},fr=(e,...t)=>{let a={page:e,params:{}};t.forEach(e=>{"string"==typeof e?a=Object.assign(Object.assign({},a),{subpage:e}):"params"in e?a=Object.assign(Object.assign({},a),{params:e.params}):"filter"in e&&(a=Object.assign(Object.assign({},a),{filter:e.filter}));});const i=e=>{let t=Object.keys(e);t=t.filter(t=>e[t]),t.sort();let a="";return t.forEach(t=>{const i=e[t];a=a.length?`${a}/${t}/${i}`:`${t}/${i}`;}),a;};let n=`/${Se}/${a.page}`;return a.subpage&&(n=`${n}/${a.subpage}`),i(a.params).length&&(n=`${n}/${i(a.params)}`),a.filter&&(n=`${n}/filter/${i(a.filter)}`),n;};var _r;!function(e){e.General="general",e.Modules="modules",e.Mappings="mappings",e.Schedules="schedules",e.Help="help";}(_r||(_r={}));const br={[_r.General]:"panels.general.title",[_r.Modules]:"panels.modules.title",[_r.Mappings]:"panels.mappings.title",[_r.Schedules]:"panels.schedules.title",[_r.Help]:"panels.help.title"};let yr=class extends de{get _activeTab(){var e;const t=null===(e=this.path)||void 0===e?void 0:e.subpage;return Object.values(_r).includes(null!=t?t:"")?t:_r.General;}_selectTab(e){Os(0,fr("setup",e));}_openWizard(){this.dispatchEvent(new CustomEvent("open-wizard",{bubbles:!0,composed:!0}));}render(){if(!this.hass)return W``;const e=this._activeTab;return W`
      <div class="setup-container">
        <nav class="setup-nav">
          ${Object.values(_r).map(t=>W`
              <button
                class="setup-nav-btn ${e===t?"active":""}"
                @click="${()=>this._selectTab(t)}"
              >
                ${Es(br[t],this.hass.language)}
              </button>
            `)}
          <button
            class="setup-nav-btn wizard-btn"
            @click="${this._openWizard}"
            title="${Es("wizard.title",this.hass.language)}"
          >
            ✦ ${Es("wizard.open_button",this.hass.language)}
          </button>
        </nav>
        <div class="setup-content">${this._renderContent(e)}</div>
      </div>
    `;}_renderContent(e){if(!this.hass)return W``;switch(e){case _r.General:return W`<smart-irrigation-view-general
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-general>`;case _r.Modules:return W`<smart-irrigation-view-modules
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-modules>`;case _r.Mappings:return W`<smart-irrigation-view-mappings
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-mappings>`;case _r.Schedules:return W`<smart-irrigation-view-schedules
          .hass="${this.hass}"
          .narrow="${this.narrow}"
        ></smart-irrigation-view-schedules>`;case _r.Help:return this._renderHelp();}}_renderHelp(){return this.hass?W`
      <ha-card
        header="${Es("panels.help.cards.how-to-get-help.title",this.hass.language)}"
      >
        <div class="card-content">
          ${Es("panels.help.cards.how-to-get-help.first-read-the",this.hass.language)}
          <a href="${"https://justchr.github.io/HAsmartirrigation/"}"
            >${Es("panels.help.cards.how-to-get-help.wiki",this.hass.language)}</a
          >.
          ${Es("panels.help.cards.how-to-get-help.if-you-still-need-help",this.hass.language)}
          <a
            href="https://community.home-assistant.io/t/smart-irrigation-save-water-by-precisely-watering-your-lawn-garden"
            >${Es("panels.help.cards.how-to-get-help.community-forum",this.hass.language)}</a
          >
          ${Es("panels.help.cards.how-to-get-help.or-open-a",this.hass.language)}
          <a href="${"https://github.com/JustChr/HAsmartirrigation/issues"}"
            >${Es("panels.help.cards.how-to-get-help.github-issue",this.hass.language)}</a
          >
          (${Es("panels.help.cards.how-to-get-help.english-only",this.hass.language)}).
        </div>
      </ha-card>
    `:W``;}static get styles(){return c`
      ${ar}

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
    `;}};var wr;n([he({attribute:!1})],yr.prototype,"hass",void 0),n([he({type:Boolean})],yr.prototype,"narrow",void 0),n([he({attribute:!1})],yr.prototype,"path",void 0),yr=n([ce("smart-irrigation-view-setup")],yr),function(e){e[e.Welcome=0]="Welcome",e[e.Weather=1]="Weather",e[e.Module=2]="Module",e[e.Mapping=3]="Mapping",e[e.Zone=4]="Zone",e[e.Done=5]="Done";}(wr||(wr={}));let kr=class extends de{constructor(){super(...arguments),this._step=wr.Welcome,this._saving=!1,this._error="",this._siConfig=null,this._useWeather=!1,this._weatherService=Me,this._apiKey="",this._testingApi=!1,this._testResult=null,this._testResultTimer=null,this._weatherConfig=null,this._availableModules=[],this._selectedModuleIndex=0,this._moduleConfig={},this._mappingName="My Sensor Group",this._tempSource=We,this._humiditySource=We,this._precipSource=We,this._zoneName="My Zone",this._zoneSize="",this._zoneThroughput="",this._zoneEntity="";}async connectedCallback(){super.connectedCallback(),await this._loadInitialData();}async _loadInitialData(){var e;if(this.hass){try{const[t,a,i]=await Promise.all([qs(this.hass),Ks(this.hass),Us(this.hass)]);this._availableModules=t,this._weatherConfig=a,this._siConfig=i,this._useWeather=a.use_weather_service,this._weatherService=null!==(e=a.weather_service)&&void 0!==e?e:Me;}catch(e){console.error("Wizard: failed to load initial data",e),this._error=Cs(e);}this.requestUpdate();}}_close(){this.dispatchEvent(new CustomEvent("wizard-close",{bubbles:!0,composed:!0}));}_navigate(e){this.dispatchEvent(new CustomEvent("wizard-navigate",{detail:{page:e},bubbles:!0,composed:!0}));}async _next(){this._error="";try{switch(this._saving=!0,this._step){case wr.Welcome:this._step=wr.Weather;break;case wr.Weather:await this._saveWeather(),this._step=wr.Module;break;case wr.Module:await this._saveModule(),this._step=wr.Mapping;break;case wr.Mapping:await this._saveMapping(),this._step=wr.Zone;break;case wr.Zone:await this._saveZone(),this._step=wr.Done;break;case wr.Done:this._close();}}catch(e){this._error=e instanceof Error?e.message:String(e);}finally{this._saving=!1,this.requestUpdate();}}_back(){this._step>wr.Welcome&&(this._step=this._step-1,this._error="");}_skipStep(){this._step<wr.Done&&(this._step=this._step+1,this._error="");}async _saveWeather(){await Js(this.hass,this._useWeather,this._useWeather?this._weatherService:null,this._apiKey||null);}async _saveModule(){if(0===this._availableModules.length)return;const e=this._availableModules[this._selectedModuleIndex],t=await Vs(this.hass,{name:e.name,description:e.description,config:Object.assign(Object.assign({},e.config),this._moduleConfig),schema:e.schema});this._savedModuleId="object"==typeof t&&(null==t?void 0:t.id)?t.id:void 0;}async _saveMapping(){const e=this._useWeather?We:Ge,t={[Ue]:{[Ke]:this._tempSource},[Ne]:{[Ke]:this._humiditySource},[He]:{[Ke]:this._precipSource}},a=["Dewpoint","Evapotranspiration","Maximum Temperature","Minimum Temperature","Current Precipitation","Pressure","Solar Radiation","Windspeed"];for(const i of a)t[i]={[Ke]:e};const i=await Ys(this.hass,{name:this._mappingName,mappings:t});this._savedMappingId="object"==typeof i&&(null==i?void 0:i.id)?i.id:void 0;}async _saveZone(){if(!this._zoneName.trim())throw new Error("Zone name is required");await Ws(this.hass,{name:this._zoneName.trim(),size:parseFloat(this._zoneSize)||0,throughput:parseFloat(this._zoneThroughput)||0,state:tr.Automatic,duration:0,bucket:0,delta:0,explanation:"",multiplier:1,module:this._savedModuleId,mapping:this._savedMappingId,lead_time:0,linked_entity:this._zoneEntity||void 0});}async _testApiKey(){if(this.hass&&!this._testingApi){this._testingApi=!0,this._testResult=null,this._testResultTimer&&clearTimeout(this._testResultTimer),this.requestUpdate();try{const e=await Xs(this.hass,this._weatherService,this._apiKey||null);this._testResult=e,this._testResultTimer=window.setTimeout(()=>{this._testResult=null,this.requestUpdate();},12e3);}catch(e){this._testResult={success:!1,error:"unknown"};}finally{this._testingApi=!1,this.requestUpdate();}}}render(){var e,t;const a=null!==(t=null===(e=this.hass)||void 0===e?void 0:e.language)&&void 0!==t?t:"en";return W`
      <div class="wizard-overlay" @click="${this._onOverlayClick}">
        <div
          class="wizard-dialog"
          @click="${e=>e.stopPropagation()}"
        >
          <div class="wizard-header">
            <span class="wizard-title">${Es("wizard.title",a)}</span>
            <button
              class="wizard-close-btn"
              @click="${this._close}"
              title="${Es("wizard.close",a)}"
            >
              ✕
            </button>
          </div>
          ${this._step!==wr.Welcome&&this._step!==wr.Done?W`<div class="wizard-stepper">${this._renderStepper()}</div>`:""}
          <div class="wizard-body">
            ${this._renderStep(a)}
            ${this._error?W`<div class="wizard-error">${this._error}</div>`:""}
          </div>
          <div class="wizard-footer">${this._renderFooter(a)}</div>
        </div>
      </div>
    `;}_onOverlayClick(e){e.target===e.currentTarget&&this._close();}_renderStepper(){const e=["Weather","Module","Sensor Group","Zone"];return W`
      ${e.map((t,a)=>{const i=a+1,n=this._step===i,s=this._step>i;return W`
          <div
            class="stepper-step ${n?"active":""} ${s?"done":""}"
          >
            <div class="stepper-circle">${s?"✓":i}</div>
            <span class="stepper-label">${t}</span>
          </div>
          ${a<e.length-1?W`<div class="stepper-line ${s?"done":""}"></div>`:""}
        `;})}
    `;}_renderStep(e){switch(this._step){case wr.Welcome:return this._renderWelcome(e);case wr.Weather:return this._renderWeather(e);case wr.Module:return this._renderModule(e);case wr.Mapping:return this._renderMapping(e);case wr.Zone:return this._renderZone(e);case wr.Done:return this._renderDone(e);default:return W``;}}_renderFooter(e){return this._step===wr.Done?W``:W`
      <div class="footer-left">
        ${this._step>wr.Welcome?W`<button
              class="wizard-btn secondary"
              @click="${this._back}"
              ?disabled="${this._saving}"
            >
              ${Es("wizard.back",e)}
            </button>`:""}
        ${this._step>wr.Welcome&&this._step<wr.Done?W`<button
              class="wizard-btn ghost"
              @click="${this._skipStep}"
              ?disabled="${this._saving}"
            >
              ${Es("wizard.skip_step",e)}
            </button>`:""}
      </div>
      <button
        class="wizard-btn primary"
        @click="${this._next}"
        ?disabled="${this._saving}"
      >
        ${this._saving?Es("common.saving-messages.saving",e):this._step===wr.Welcome||this._step<wr.Zone?Es("wizard.next",e):Es("wizard.finish",e)}
      </button>
    `;}_renderWelcome(e){return W`
      <h2 class="step-title">
        ${Es("wizard.steps.welcome.title",e)}
      </h2>
      <p class="step-desc">${Es("wizard.steps.welcome.intro",e)}</p>
      <ul class="step-list">
        <li>① ${Es("wizard.steps.welcome.step1_label",e)}</li>
        <li>② ${Es("wizard.steps.welcome.step2_label",e)}</li>
        <li>③ ${Es("wizard.steps.welcome.step3_label",e)}</li>
        <li>④ ${Es("wizard.steps.welcome.step4_label",e)}</li>
      </ul>
      <p class="step-tip">${Es("wizard.steps.welcome.tip",e)}</p>
    `;}_renderWeather(e){var t,a,i,n,s;const r=[Me],o=this._useWeather&&!r.includes(this._weatherService);return W`
      <h2 class="step-title">
        ${Es("wizard.steps.weather.title",e)}
      </h2>
      <p class="step-desc">
        ${Es("wizard.steps.weather.description",e)}
      </p>

      <si-field
        label="${Es("weather_service_config.enabled_label",e)}"
      >
        <ha-switch
          .checked="${this._useWeather}"
          @change="${e=>{this._useWeather=e.target.checked;}}"
        ></ha-switch>
      </si-field>

      ${this._useWeather?W`
            <si-field
              label="${Es("weather_service_config.service_label",e)}"
            >
              <select
                class="wizard-input"
                .value="${this._weatherService}"
                @change="${e=>{this._weatherService=e.target.value,this._testResult=null;}}"
              >
                <option
                  value="${Me}"
                  ?selected="${this._weatherService===Me}"
                >
                  ${Es("weather_service_config.openmeteo",e)}
                </option>
                <option
                  value="${$e}"
                  ?selected="${this._weatherService===$e}"
                >
                  ${Es("weather_service_config.owm",e)}
                </option>
                <option
                  value="${Ae}"
                  ?selected="${this._weatherService===Ae}"
                >
                  ${Es("weather_service_config.pw",e)}
                </option>
              </select>
            </si-field>

            ${o?W`
                  <si-field
                    label="${Es("weather_service_config.api_key_label",e)}"
                    help="${Es("weather_service_config.api_key_help",e)}"
                  >
                    ${(this._weatherService===$e?null===(t=this._weatherConfig)||void 0===t?void 0:t.has_owm_api_key:this._weatherService===Ae&&(null===(a=this._weatherConfig)||void 0===a?void 0:a.has_pw_api_key))?W`<span class="api-badge configured"
                          >${Es("weather_service_config.api_key_configured",e)}</span
                        >`:""}
                    <div class="api-row">
                      <input
                        type="password"
                        class="wizard-input flex1"
                        placeholder="${Es("weather_service_config.api_key_placeholder",e)}"
                        .value="${this._apiKey}"
                        @input="${e=>{this._apiKey=e.target.value,this._testResult=null;}}"
                      />
                      <button
                        class="wizard-btn secondary"
                        type="button"
                        ?disabled="${this._testingApi||!this._apiKey&&!(this._weatherService===$e?null===(i=this._weatherConfig)||void 0===i?void 0:i.has_owm_api_key:this._weatherService===Ae&&(null===(n=this._weatherConfig)||void 0===n?void 0:n.has_pw_api_key))}"
                        @click="${this._testApiKey}"
                      >
                        ${this._testingApi?Es("weather_service_config.test_button_testing",e):Es("weather_service_config.test_button",e)}
                      </button>
                    </div>
                    ${null!==this._testResult?W`
                          <div
                            class="test-result ${this._testResult.success?"success":"error"}"
                          >
                            ${this._testResult.success?Es("weather_service_config.test_success",e):Es("weather_service_config.test_error_"+(null!==(s=this._testResult.error)&&void 0!==s?s:"unknown"),e)}
                          </div>
                        `:""}
                  </si-field>
                `:W`
                  <div class="info-note">
                    ${Es("weather_service_config.no_api_key_needed",e)}
                  </div>
                `}
          `:""}
    `;}_renderModule(e){if(0===this._availableModules.length)return W`
        <h2 class="step-title">
          ${Es("wizard.steps.module.title",e)}
        </h2>
        <p class="step-desc">
          ${Es("wizard.steps.module.no_modules",e)}
        </p>
      `;const t=this._availableModules[this._selectedModuleIndex];return W`
      <h2 class="step-title">${Es("wizard.steps.module.title",e)}</h2>
      <p class="step-desc">
        ${Es("wizard.steps.module.description",e)}
      </p>

      <si-field
        label="${Es("wizard.steps.module.pick_label",e)}"
        required
      >
        <select
          class="wizard-input"
          @change="${e=>{this._selectedModuleIndex=parseInt(e.target.value),this._moduleConfig={};}}"
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
    `;}_renderModuleField(e,t){var a,i;const n=e.replace(/_/g," ").replace(/\b\w/g,e=>e.toUpperCase()),s=null!==(i=null!==(a=this._moduleConfig[e])&&void 0!==a?a:t.default)&&void 0!==i?i:"",r=t.description;return"boolean"===t.type?W`
        <si-field label="${n}" help="${null!=r?r:""}">
          <ha-switch
            .checked="${Boolean(s)}"
            @change="${t=>{this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:t.target.checked});}}"
          ></ha-switch>
        </si-field>
      `:"select"===t.type&&t.options?W`
        <si-field label="${n}" help="${null!=r?r:""}">
          <select
            class="wizard-input"
            @change="${t=>{this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:t.target.value});}}"
          >
            ${t.options.map(([e,t])=>W`<option
                  value="${e}"
                  ?selected="${e===String(s)}"
                >
                  ${t}
                </option>`)}
          </select>
        </si-field>
      `:W`
      <si-field label="${n}" help="${null!=r?r:""}">
        <input
          type="${"float"===t.type||"integer"===t.type?"number":"text"}"
          class="wizard-input"
          step="${"float"===t.type?"0.01":"1"}"
          .value="${String(s)}"
          @input="${a=>{const i=a.target.value,n="float"===t.type?parseFloat(i):"integer"===t.type?parseInt(i):i;this._moduleConfig=Object.assign(Object.assign({},this._moduleConfig),{[e]:n});}}"
        />
      </si-field>
    `;}_renderMapping(e){const t=[{value:We,label:Es("wizard.steps.mapping.use_weather_service",e)},{value:"sensor",label:Es("wizard.steps.mapping.use_sensor",e)},{value:"static",label:Es("wizard.steps.mapping.use_static",e)},{value:Ge,label:Es("wizard.steps.mapping.use_none",e)}],a=(a,i,n)=>W`
      <si-field
        label="${Es("wizard.steps.mapping.source_label",e)} ${a}"
      >
        <select
          class="wizard-input"
          @change="${e=>n(e.target.value)}"
        >
          ${t.map(e=>W`<option value="${e.value}" ?selected="${e.value===i}">
                ${e.label}
              </option>`)}
        </select>
      </si-field>
    `;return W`
      <h2 class="step-title">
        ${Es("wizard.steps.mapping.title",e)}
      </h2>
      <p class="step-desc">
        ${Es("wizard.steps.mapping.description",e)}
      </p>

      <si-field
        label="${Es("wizard.steps.mapping.name_label",e)}"
        required
      >
        <input
          type="text"
          class="wizard-input"
          .value="${this._mappingName}"
          @input="${e=>{this._mappingName=e.target.value;}}"
        />
      </si-field>

      ${a(Es("panels.mappings.cards.mapping.items.temperature",e)||"Temperature",this._tempSource,e=>{this._tempSource=e,this.requestUpdate();})}
      ${a(Es("panels.mappings.cards.mapping.items.humidity",e)||"Humidity",this._humiditySource,e=>{this._humiditySource=e,this.requestUpdate();})}
      ${a(Es("panels.mappings.cards.mapping.items.precipitation",e)||"Precipitation",this._precipSource,e=>{this._precipSource=e,this.requestUpdate();})}

      <p class="step-tip">
        ${Es("wizard.steps.mapping.description",e)}
      </p>
    `;}_renderZone(e){var t;const a="imperial"!==(null===(t=this._siConfig)||void 0===t?void 0:t.units),i=a?"m²":at,n=a?it:nt;return W`
      <h2 class="step-title">${Es("wizard.steps.zone.title",e)}</h2>
      <p class="step-desc">
        ${Es("wizard.steps.zone.description",e)}
      </p>

      <si-field
        label="${Es("wizard.steps.zone.name_label",e)}"
        required
      >
        <input
          type="text"
          class="wizard-input"
          .value="${this._zoneName}"
          @input="${e=>{this._zoneName=e.target.value;}}"
        />
      </si-field>

      <si-field
        label="${Es("wizard.steps.zone.size_label",e)}"
        unit="${i}"
        help="${Es("field_help.zone_size",e)}"
      >
        <input
          type="number"
          class="wizard-input"
          min="0"
          step="0.1"
          .value="${this._zoneSize}"
          @input="${e=>{this._zoneSize=e.target.value;}}"
        />
      </si-field>

      <si-field
        label="${Es("wizard.steps.zone.throughput_label",e)}"
        unit="${n}"
        help="${Es("field_help.zone_throughput",e)}"
      >
        <input
          type="number"
          class="wizard-input"
          min="0"
          step="0.1"
          .value="${this._zoneThroughput}"
          @input="${e=>{this._zoneThroughput=e.target.value;}}"
        />
      </si-field>

      <si-field
        label="${Es("wizard.steps.zone.entity_label",e)}"
        help="${Es("field_help.zone_linked_entity",e)}"
      >
        <ha-entity-picker
          .hass="${this.hass}"
          .value="${this._zoneEntity}"
          .includeDomains="${["switch","valve"]}"
          allow-custom-entity
          @value-changed="${e=>{this._zoneEntity=e.detail.value||"";}}"
        ></ha-entity-picker>
      </si-field>
    `;}_renderDone(e){return W`
      <div class="done-wrapper">
        <div class="done-icon">✓</div>
        <h2 class="step-title">${Es("wizard.steps.done.title",e)}</h2>
        <p class="step-desc">
          ${Es("wizard.steps.done.description",e)}
        </p>
        <ul class="step-list">
          <li>${Es("wizard.steps.done.tip1",e)}</li>
          <li>${Es("wizard.steps.done.tip2",e)}</li>
          <li>${Es("wizard.steps.done.tip3",e)}</li>
        </ul>
        <div class="done-actions">
          <button
            class="wizard-btn primary"
            @click="${()=>{this._close(),this._navigate("zones");}}"
          >
            ${Es("wizard.steps.done.go_zones",e)}
          </button>
          <button
            class="wizard-btn secondary"
            @click="${()=>{this._close(),this._navigate("setup");}}"
          >
            ${Es("wizard.steps.done.go_setup",e)}
          </button>
        </div>
      </div>
    `;}static get styles(){return c`
      ${ar}

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
        font-size: 1rem;
        padding: 4px 8px;
        border-radius: 4px;
        transition: background 0.15s;
      }

      .wizard-close-btn:hover {
        background: var(--secondary-background-color);
        color: var(--primary-text-color);
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
        font-size: 3rem;
        color: #4caf50;
        margin-bottom: 12px;
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
    `;}};n([he({attribute:!1})],kr.prototype,"hass",void 0),n([ge()],kr.prototype,"_step",void 0),n([ge()],kr.prototype,"_saving",void 0),n([ge()],kr.prototype,"_error",void 0),n([ge()],kr.prototype,"_siConfig",void 0),n([ge()],kr.prototype,"_useWeather",void 0),n([ge()],kr.prototype,"_weatherService",void 0),n([ge()],kr.prototype,"_apiKey",void 0),n([ge()],kr.prototype,"_testingApi",void 0),n([ge()],kr.prototype,"_testResult",void 0),n([ge()],kr.prototype,"_availableModules",void 0),n([ge()],kr.prototype,"_selectedModuleIndex",void 0),n([ge()],kr.prototype,"_moduleConfig",void 0),n([ge()],kr.prototype,"_mappingName",void 0),n([ge()],kr.prototype,"_tempSource",void 0),n([ge()],kr.prototype,"_humiditySource",void 0),n([ge()],kr.prototype,"_precipSource",void 0),n([ge()],kr.prototype,"_zoneName",void 0),n([ge()],kr.prototype,"_zoneSize",void 0),n([ge()],kr.prototype,"_zoneThroughput",void 0),n([ge()],kr.prototype,"_zoneEntity",void 0),kr=n([ce("si-setup-wizard")],kr);const zr=ar;var Sr;!function(e){e.Zones="zones",e.Setup="setup";}(Sr||(Sr={})),e.SmartIrrigationPanel=class extends de{constructor(){super(...arguments),this._wizardOpen=!1,this._updateScheduled=!1,this._lastNavigationTime=0,this._navigationThrottleDelay=100;}_scheduleUpdate(){this._updateScheduled||(this._updateScheduled=!0,requestAnimationFrame(()=>{this._updateScheduled=!1,this.requestUpdate();}));}async firstUpdated(){Os(0,fr(Sr.Zones)),window.addEventListener("location-changed",()=>{if(!window.location.pathname.includes("smart-irrigation"))return;const e=performance.now();e-this._lastNavigationTime<this._navigationThrottleDelay||(this._lastNavigationTime=e,this._scheduleUpdate());}),be().then(()=>{this._scheduleUpdate();}).catch(e=>{console.error("Failed to load HA form elements:",e),this._scheduleUpdate();});}render(){const e=vr(),t=!!customElements.get("ha-tab-group"),a=!!customElements.get("ha-tab-group-tab");return W`
      <div class="header">
        <div class="toolbar">
          <ha-menu-button
            .hass=${this.hass}
            .narrow=${this.narrow}
          ></ha-menu-button>
          <div class="main-title">${Es("title",this.hass.language)}</div>
          <div class="version">${ze}</div>
        </div>

        ${t&&a?W`
              <ha-tab-group @wa-tab-show=${this.handlePageSelected}>
                ${Object.values(Sr).map(t=>W`
                    <ha-tab-group-tab
                      slot="nav"
                      panel="${t}"
                      .active=${e.page===t}
                    >
                      ${Es(`panels.${t}.title`,this.hass.language)}
                    </ha-tab-group-tab>
                  `)}
              </ha-tab-group>
            `:W`
              <div class="custom-tabs">
                ${Object.values(Sr).map(t=>W`
                    <button
                      class="custom-tab ${e.page===t?"active":""}"
                      @click=${()=>this.navigateToPage(t)}
                    >
                      ${Es(`panels.${t}.title`,this.hass.language)}
                    </button>
                  `)}
              </div>
            `}
      </div>
      <div class="view">${this.getView(e)}</div>
      ${this._wizardOpen?W`
            <si-setup-wizard
              .hass="${this.hass}"
              @wizard-close="${()=>{this._wizardOpen=!1;}}"
              @wizard-navigate="${e=>{var t,a;const i=null!==(a=null===(t=e.detail)||void 0===t?void 0:t.page)&&void 0!==a?a:"zones";this._wizardOpen=!1,this.navigateToPage(i);}}"
            ></si-setup-wizard>
          `:""}
    `;}getView(e){switch(e.page){case"zones":default:return W`
          <smart-irrigation-view-zones
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${e}
            @open-wizard="${()=>{this._wizardOpen=!0;}}"
          ></smart-irrigation-view-zones>
        `;case"setup":return W`
          <smart-irrigation-view-setup
            .hass=${this.hass}
            .narrow=${this.narrow}
            .path=${e}
            @open-wizard="${()=>{this._wizardOpen=!0;}}"
          ></smart-irrigation-view-setup>
        `;}}navigateToPage(e){if(e!==vr().page){const t=fr(e);Os(0,t),this.requestUpdate();}else scrollTo(0,0);}handlePageSelected(e){const t=e.detail.name;if(t!==vr().page){const e=fr(t);Os(0,e),this.requestUpdate();}else scrollTo(0,0);}static get styles(){return[zr,c`
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
          max-width: 960px;
        }

        .view > *:last-child {
          margin-bottom: 20px;
        }

        .version {
          font-size: 14px;
          font-weight: 500;
          color: rgba(var(--rgb-text-primary-color), 0.9);
        }
      `];}},n([he({attribute:!1})],e.SmartIrrigationPanel.prototype,"hass",void 0),n([he({type:Boolean,reflect:!0})],e.SmartIrrigationPanel.prototype,"narrow",void 0),n([ge()],e.SmartIrrigationPanel.prototype,"_wizardOpen",void 0),e.SmartIrrigationPanel=n([ce("smart-irrigation")],e.SmartIrrigationPanel);let xr=class extends de{async showDialog(e){this._params=e,await this.updateComplete;}async closeDialog(){this._params=void 0;}render(){return this._params?W`
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
              .path=${"M19,6.41L17.59,5L12,10.59L6.41,5L5,6.41L10.59,12L5,17.59L6.41,19L12,13.41L17.59,19L19,17.59L13.41,12L19,6.41Z"}
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
    `:W``;}static get styles(){return c`
      div.wrapper {
        color: var(--primary-text-color);
      }
      span.errortitle {
        font-size: 2em;
        font-weight: bold;
        vertical-align: bottom;
      }
    `;}};n([he({attribute:!1})],xr.prototype,"hass",void 0),n([ge()],xr.prototype,"_params",void 0),xr=n([ce("error-dialog")],xr);var $r=Object.freeze({__proto__:null,get ErrorDialog(){return xr;}});Object.defineProperty(e,"__esModule",{value:!0});}({});
