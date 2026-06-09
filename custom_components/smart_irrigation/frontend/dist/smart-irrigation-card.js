!function () {
  "use strict";

  const t = `v${"2026.06.14"}`;
  let i;
  class s extends HTMLElement {
    setConfig(t) {
      this._config = t, this._mount();
    }
    set hass(t) {
      this._hass = t, this._inner && (this._inner.hass = t);
    }
    getCardSize() {
      return 6;
    }
    getGridOptions() {
      return {
        columns: "full",
        rows: "auto",
        min_columns: 6
      };
    }
    static getStubConfig() {
      return {};
    }
    async _mount() {
      var t, s;
      await function () {
        i || (i = import("/smart_irrigation_card/smart-irrigation-card-impl.js"));
        return i;
      }(), this._inner || (this._inner = document.createElement("smart-irrigation-zones-card-impl"), this.appendChild(this._inner)), this._hass && (this._inner.hass = this._hass), this._config && (null === (s = (t = this._inner).setConfig) || void 0 === s || s.call(t, this._config));
    }
  }
  customElements.get("smart-irrigation-zones-card") || customElements.define("smart-irrigation-zones-card", s);
  const n = window;
  n.customCards = n.customCards || [], n.customCards.some(t => "smart-irrigation-zones-card" === t.type) || (n.customCards.push({
    type: "smart-irrigation-zones-card",
    name: "Smart Irrigation Zones",
    description: "Everyday zone status and manual irrigation, usable by non-admin users.",
    preview: !1
  }), console.info(`%c smart-irrigation-zones-card %c ${t} `, "color: white; background: #3949ab; font-weight: 700;", "color: #3949ab; background: white; font-weight: 700;"));
}();
