/** @odoo-module */

import {Component, onWillStart, onMounted, useRef} from '@odoo/owl'
import {registry} from '@web/core/registry'
import {useInputField} from '@web/views/fields/input_field_hook';
import {standardFieldProps} from "@web/views/fields/standard_field_props";
import {loadJS, loadCSS} from "@web/core/assets";


export class ToolbarWidget extends Component {
    static template = 'spiffy_theme_backend.toolbar';
    static props = {
        ...standardFieldProps,
        placeholder: {type: String, optional: true},
    };

    setup() {
        this.editor = useRef("editor")
        onWillStart(async () => {
            await loadJS("https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.js")
            await loadCSS("https://cdn.jsdelivr.net/npm/quill@2.0.2/dist/quill.snow.css")
        })
        onMounted(() => {
            const quill = new Quill(this.editor.el, {
                theme: 'snow',
                placeholder: this.props.placeholder || 'Write something...'

            });
            quill.root.innerHTML = this.props.record.data[this.props.name] || "";

        })
        useInputField({getValue: () => this.props.record.data[this.props.name] || ""});
    }

    onInput(event) {
        const value = event.target.innerHTML;
        console.log('value', value)
        this.props.record.data[this.props.name] = value;
        this.props.record.update({[this.props.name]: value});
    }
}

export const toolbarWidget = {
    component: ToolbarWidget,
    displayName: ("toolbar"),
    supportedTypes: ["html", "text"],
    extractProps: ({attrs}) => ({
        placeholder: attrs.placeholder,

    }),
};

registry.category("fields").add("toolbar", toolbarWidget);

