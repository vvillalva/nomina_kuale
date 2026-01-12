/** @odoo-module **/
import {CharField} from "@web/views/fields/char/char_field";
import {registry} from "@web/core/registry";
import {archParseBoolean} from "@web/views/utils";
import {_t} from "@web/core/l10n/translation";
import {useSpecialData} from "@web/views/fields/relational_utils";
import {standardFieldProps} from "@web/views/fields/standard_field_props";


export class FormWidget extends CharField {
    static props = {
        ...standardFieldProps,
        placeholder: {type: String, optional: true},
        required: {type: Boolean, optional: true},
        domain: {type: Array, optional: true},
        autosave: {type: Boolean, optional: true},
    };
    static defaultProps = {
        autosave: false,
    };

    setup() {
        super.setup();
        this.type = this.props.record.fields[this.props.name].type;
        if (this.type === "many2one") {
            this.specialData = useSpecialData((orm, props) => {
                const {relation} = props.record.fields[props.name];
                return orm.call(relation, "name_search", ["", props.domain]);
            });
        }
    }

    get options() {
        switch (this.type) {
            case "many2one":
                return [...this.specialData.data];
            case "selection":
                return this.props.record.fields[this.props.name].selection.filter(
                    (option) => option[0] !== false && option[1] !== ""
                );
            default:
                return [];
        }
    }

    get string() {
        switch (this.type) {
            case "many2one":
                return this.props.record.data[this.props.name]
                    ? this.props.record.data[this.props.name][1]
                    : "";
            case "selection":
                return this.props.record.data[this.props.name] !== false
                    ? this.options.find((o) => o[0] === this.props.record.data[this.props.name])[1]
                    : "";
            default:
                return "";
        }
    }

    get value() {
        const rawValue = this.props.record.data[this.props.name];
        return this.type === "many2one" && rawValue ? rawValue[0] : rawValue;
    }

    stringify(value) {
        return JSON.stringify(value);
    }

    /**
     * @param {Event} ev
     */
    onChange(ev) {
        const value = JSON.parse(ev.target.value);
        switch (this.type) {
            case "many2one":
                if (value === false) {
                    this.props.record.update(
                        {[this.props.name]: false},
                        {save: this.props.autosave}
                    );
                } else {
                    this.props.record.update(
                        {
                            [this.props.name]: this.options.find((option) => option[0] === value),
                        },
                        {save: this.props.autosave}
                    );
                }
                break;
            case "selection":
                this.props.record.update(
                    {[this.props.name]: value},
                    {save: this.props.autosave}
                );
                break;
        }
    }

}

FormWidget.template = "spiffy_theme_backend.formWidget"


registry.category("fields").add("form_widget", {
    component: FormWidget,
    displayName: "Readonly Widget",
    supportedTypes: ["char", "text", "many2one", "selection"],
    supportedOptions: [
        {
            label: _t("Dynamic placeholder"),
            name: "dynamic_placeholder",
            type: "boolean",
            help: _t("Enable this option to allow the input to display a dynamic placeholder."),
        },
        {
            label: _t("Model reference field"),
            name: "dynamic_placeholder_model_reference_field",
            type: "field",
            availableTypes: ["char"],
        },
    ],
    extractProps: ({attrs, options}) => ({
        isPassword: archParseBoolean(attrs.password),
        dynamicPlaceholder: options.dynamic_placeholder || false,
        dynamicPlaceholderModelReferenceField:
            options.dynamic_placeholder_model_reference_field || "",
        autocomplete: attrs.autocomplete,
        placeholder: attrs.placeholder,
    }),
});


