/** @odoo-module **/

import {registry} from "@web/core/registry";
import {SelectionField} from "@web/views/fields/selection/selection_field"

export class CustomSelect extends SelectionField{}

CustomSelect.template= 'spiffy_theme_backend.customSelection'

registry.category("fields").add("custom_select", {
    component: CustomSelect,
    displayName: "Custom select",
    supportedTypes: ["many2one", "selection"],
});