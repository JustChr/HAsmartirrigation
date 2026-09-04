/**
 * Backwards-compatibility shim for the pre-#120 card type.
 *
 * Dashboards written before the rename say `type: custom:smart-irrigation-zones-card`.
 * That tag now belongs to the *other* project, so claiming it unconditionally is
 * exactly the collision the rename exists to remove.
 *
 * The decision therefore is NOT made here. `panel.py` serves this bundle only
 * when no foreign `smart_irrigation` integration is installed, so in the one
 * case where the old tag is genuinely unowned we keep existing dashboards
 * working, and in the case where upstream owns it we never load at all.
 *
 * Registering the same class under two tags is not possible — a constructor may
 * only be registered once — so the legacy tag gets a trivial subclass. It
 * inherits every behaviour of the real stub, including the lazy import of the
 * heavy implementation bundle.
 */
import "./irrigation-plus-card";

const CURRENT_TAG = "irrigation-plus-zones-card";
const LEGACY_TAG = "smart-irrigation-zones-card";

const current = customElements.get(CURRENT_TAG);

if (current && !customElements.get(LEGACY_TAG)) {
  // The guard matters: if anything else already owns the legacy tag, defining
  // it again throws and takes down every card on the page. Yielding is always
  // the safer half of that trade — a card that renders someone else's content
  // is a bug, a page that fails to render at all is worse.
  customElements.define(LEGACY_TAG, class extends current {});

  console.info(
    `%c ${LEGACY_TAG} %c is deprecated; update your dashboards to ${CURRENT_TAG} `,
    "color: white; background: #f4a460; font-weight: 700;",
    "color: #f4a460; background: white; font-weight: 700;",
  );
}
