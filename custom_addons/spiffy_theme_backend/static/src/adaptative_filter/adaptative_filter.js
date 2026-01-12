/** @odoo-module **/

import {ListRenderer} from "@web/views/list/list_renderer";
import {ListController} from "@web/views/list/list_controller";
import {listView} from "@web/views/list/list_view";
import {registry} from "@web/core/registry";
import {onMounted, useRef} from "@odoo/owl";
import {patch} from "@web/core/utils/patch";
import {SearchModel} from "@web/search/search_model";
import {domainFromTree, treeFromDomain} from "@web/core/tree_editor/condition_tree";

console.log("📌 CustomListRenderer cargado");

class CustomListRenderer extends ListRenderer {
    setup() {
        super.setup();
        console.log("✅ CustomListRenderer: setup ejecutado");
        this.tableRef = useRef("table");
        this.activeFilters = {}; // Guardará los filtros aplicados
        this.filterToggleCounter = 0;

        onMounted(() => {

            const buttonsContainer = document.querySelector(".o_cp_searchview");
            const searchDropdown = buttonsContainer.querySelector(".o-dropdown.o-dropdown--no-caret");

            if (buttonsContainer) {
                const toggleFiltersButton = document.createElement("button");
                toggleFiltersButton.classList.add("dropdown-toggle", "o_searchview_dropdown_toggler", "d-print-none", "btn", "btn-outline-secondary", "o-no-caret", "rounded-start-0", "h-100");
                toggleFiltersButton.innerHTML = `<i class="fa fa-cogs" aria-hidden="true"></i>`
                searchDropdown.appendChild(toggleFiltersButton)

                toggleFiltersButton.addEventListener("click", () => {
                    this._toggleFilters();
                })
            }

        });
    }


    _toggleFilters() {
        this.filterToggleCounter++;

        // Si el contador es impar, añadimos los filtros
        if (this.filterToggleCounter % 2 !== 0) {
            this._addFilterInputs();
        } else {
            this._removeFilterInputs();
        }
    }

    async _addFilterInputs() {


        console.log("🎯 Agregando fila de filtros en el encabezado");

        const thead = this.tableRef.el.querySelector("thead");
        if (!thead) return;

        const filterRow = document.createElement("tr");
        filterRow.classList.add("custom-filter-row");
        const emptyTh = document.createElement("th");
        emptyTh.innerHTML = `<i class="me-2 text-primary fa fa-filter"></i>`
        filterRow.appendChild(emptyTh);

        this.state.columns.forEach((column) => {
            const th = document.createElement("th");
            th.classList.add("custom-filter-container");

            const filterWrapper = document.createElement("div");
            filterWrapper.classList.add("filter-wrapper");

            const input = document.createElement("input");
            console.log('ct:', column)
            console.log('ct2: ', column.field.supportedTypes)


            input.type = "text";
            input.classList.add("custom-filter-input");
            input.placeholder = `Filtrar ${column.string}`;
            input.dataset.field = column.name;

            const button = document.createElement("button");
            button.innerHTML = `<i class="fa fa-caret-down"></i>`;
            button.classList.add("custom-filter-btn");
            button.dataset.field = column.name;
            button.addEventListener("click", (event) => this._toggleFilterPopup(event, column.name));

            input.addEventListener("keydown", (event) => {
                if (event.key === "Enter") {
                    this._onFilterChange(event, column.name);
                }
            });

            filterWrapper.appendChild(input);
            filterWrapper.appendChild(button);
            th.appendChild(filterWrapper);
            filterRow.appendChild(th);
        });
        const extraElement = document.querySelector('.o_list_controller.o_list_actions_header.position-sticky.end-0')
        if (extraElement) {
            const emptyTh2 = document.createElement("th");
            filterRow.appendChild(emptyTh2);
        }
        thead.appendChild(filterRow);
    }

    _removeFilterInputs() {
        const filterRow = document.querySelector(".custom-filter-row");
        if (filterRow) {
            filterRow.remove();
        }
    }

    _toggleFilterPopup(event, fieldName) {
        event.stopPropagation();

        let existingPopup = document.querySelector(".custom-filter-popup");
        if (existingPopup) existingPopup.remove();

        const popup = document.createElement("div");
        popup.classList.add("custom-filter-popup");

        const divText = document.createElement('div')
        divText.classList.add('custom-filter-row-popup-2')
        divText.innerHTML = `<div>Filtrando por las siguientes reglas:</div>`
        const filterList = document.createElement("div");
        filterList.classList.add("custom-filter-list");


        if (!this.appliedFilters) {
            this.appliedFilters = {};
        }
        if (!this.appliedFilters[fieldName]) {
            this.appliedFilters[fieldName] = [];
        }

        const input = document.querySelector(`.custom-filter-input[data-field="${fieldName}"]`);
        if (input && input.value.trim()) {
            let filter = [fieldName, "ilike", input.value.trim()];

            if (!this.appliedFilters[fieldName].some(f => f[2] === filter[2])) {
                this.appliedFilters[fieldName].push(filter);
            }

            input.value = "";
        }

        if (this.appliedFilters[fieldName].length) {
            this.appliedFilters[fieldName].forEach(filter => this._addFilterRow(filterList, fieldName, filter));
        } else {
            this._addFilterRow(filterList, fieldName);
        }

        const buttonContainer = document.createElement("div");
        buttonContainer.classList.add("custom-filter-buttons_main");

        const leftButtonContainer = document.createElement('div');
        leftButtonContainer.classList.add("custom-filter-buttons");

        const rightButtonContainer = document.createElement('div');
        rightButtonContainer.classList.add("custom-filter-buttons");

        const clearButton = document.createElement("button");
        clearButton.classList.add("btn", "btn-outline-danger");
        clearButton.innerText = "Limpiar";
        clearButton.addEventListener("click", () => this._clearFilters(filterList, fieldName));

        const resetButton = document.createElement("button");
        resetButton.classList.add("btn", "btn-outline-secondary");
        resetButton.innerText = "Reset";
        resetButton.addEventListener("click", () => this._resetFilters(filterList, fieldName));

        const closeButton = document.createElement("button");
        closeButton.classList.add("btn", "btn-outline-secondary");
        closeButton.innerText = "Cerrar";
        closeButton.addEventListener("click", () => popup.remove());

        const applyButton = document.createElement("button");
        applyButton.classList.add("btn", "btn-outline-primary");
        applyButton.innerText = "Aplicar";
        applyButton.addEventListener("click", () => this._applyFilters(fieldName, popup));

        leftButtonContainer.appendChild(clearButton);
        leftButtonContainer.appendChild(resetButton);
        rightButtonContainer.appendChild(closeButton);
        rightButtonContainer.appendChild(applyButton);

        buttonContainer.appendChild(leftButtonContainer);
        buttonContainer.appendChild(rightButtonContainer);

        popup.appendChild(divText);
        popup.appendChild(filterList);
        popup.appendChild(buttonContainer);
        document.body.appendChild(popup);

        const rect = event.target.getBoundingClientRect();
        const screenWidth = window.innerWidth;
        const popupWidth = popup.offsetWidth;
        const leftPosition = rect.right + window.scrollX + 10;

        if (leftPosition <= 300) {
            popup.style.left = '300px';
        } else {
            popup.style.left = `${leftPosition}px`;
        }

        popup.style.top = `${rect.bottom + window.scrollY}px`;

        popup.addEventListener("click", (e) => e.stopPropagation());

        document.addEventListener("click", () => popup.remove(), {once: true});
    }

    _addFilterRow(filterList, fieldName, existingFilter = null) {
        const filterRow = document.createElement("div");
        filterRow.classList.add("custom-filter-row-popup");
        filterRow.style.display = 'flex'
        filterRow.style.gap = '5px'

        const select = document.createElement("select");
        select.classList.add("custom-filter-condition");
        select.classList.add("form-select");
        select.innerHTML = `
            <option value="ilike">Contiene</option>
            <option value="=">Igual a</option>
            <option value=">">Mayor que</option>
            <option value="<">Menor que</option>
        `;

        const input = document.createElement("input");
        input.type = "text";
        input.classList.add("custom-filter-value");
        input.classList.add("form-control");
        input.placeholder = "Valor";

        if (existingFilter) {
            select.value = existingFilter[1];
            input.value = existingFilter[2];
        }

        const addButton = document.createElement("button");
        addButton.classList.add("custom-filter-add");
        addButton.innerHTML = `<i class="fa fa-plus"></i>`;
        addButton.addEventListener("click", () => this._addFilterRow(filterList, fieldName));

        const removeButton = document.createElement("button");
        removeButton.classList.add("custom-filter-remove");
        removeButton.innerHTML = `<i class="fa fa-trash"></i>`;
        removeButton.addEventListener("click", () => filterRow.remove());

        filterRow.appendChild(select);
        filterRow.appendChild(input);
        filterRow.appendChild(addButton);
        filterRow.appendChild(removeButton);
        filterList.appendChild(filterRow);
    }

    async _clearFilters(filterList, fieldName) {
        console.log(`🗑 Limpiando todas las reglas del campo: ${fieldName}`);


        if (this.appliedFilters && this.appliedFilters[fieldName]) {
            delete this.appliedFilters[fieldName];
        }

        filterList.innerHTML = "";

        this._addFilterRow(filterList, fieldName);

        let cleanFilters = [];
        Object.keys(this.appliedFilters || {}).forEach((key) => {
            cleanFilters = [...cleanFilters, ...this.appliedFilters[key]];
        });

        let finalDomain = [];
        if (cleanFilters.length > 1) {
            for (let i = 1; i < cleanFilters.length; i++) {
                finalDomain.push("&");
            }
        }
        finalDomain.push(...cleanFilters);

        console.log("✅ Dominio actualizado después de `Clear`:", finalDomain);

        await this.env.searchModel.replaceDomain(finalDomain);
    }

    _resetFilters(filterList, fieldName) {
        console.log(`♻️ Reset: Eliminando reglas NO aplicadas para: ${fieldName}`);

        if (!this.appliedFilters || !this.appliedFilters[fieldName]) {
            console.log("⚠️ No hay reglas aplicadas aún.");
            return;
        }

        // 🔹 Obtener reglas aplicadas en formato comparable
        const appliedRules = this.appliedFilters[fieldName].map(f => JSON.stringify(f));

        // 🔹 Recorrer las reglas del popup y eliminar las NO aplicadas
        filterList.querySelectorAll(".custom-filter-row-popup").forEach((row) => {
            const condition = row.querySelector(".custom-filter-condition").value;
            const value = row.querySelector(".custom-filter-value").value.trim();
            const rule = JSON.stringify([fieldName, condition, value]);

            // 🔥 Si la regla NO está en `appliedFilters`, la eliminamos
            if (!appliedRules.includes(rule)) {
                row.remove();
            }
        });

        console.log("✅ Reset ejecutado correctamente.");
    }

    async _applyFilters(fieldName, popup) {
        const filterRows = popup.querySelectorAll(".custom-filter-row-popup");
        let newFilters = [];

        this.activeFilters[fieldName] = []; // Limpiar filtros previos del campo actual

        // 🔹 **Extraer condiciones (field, operador, valor)**
        filterRows.forEach((row) => {
            const condition = row.querySelector(".custom-filter-condition").value;
            const value = row.querySelector(".custom-filter-value").value.trim();
            if (value) {
                let filter = [fieldName, condition, value];
                newFilters.push(filter);
                this.activeFilters[fieldName].push(filter);
            }
        });

        // 🔹 **Actualizar `appliedFilters` con los nuevos filtros**
        if (!this.appliedFilters) {
            this.appliedFilters = {};
        }
        this.appliedFilters[fieldName] = newFilters;

        // ❌ **Eliminar los campos vacíos de `appliedFilters`**
        for (const key in this.appliedFilters) {
            if (this.appliedFilters[key].length === 0) {
                delete this.appliedFilters[key]; // Eliminar campos sin filtros
            }
        }

        // 🔹 **Obtener el dominio actual y limpiarlo**
        let cleanFilters = [];
        Object.keys(this.appliedFilters).forEach((key) => {
            cleanFilters = [...cleanFilters, ...this.appliedFilters[key]];
        });

        console.log('🧹 Dominio actual limpio:', cleanFilters);

        // ✅ **Construcción del `finalDomain` con `"&"`**
        let finalDomain = [];
        if (cleanFilters.length > 1) {
            for (let i = 1; i < cleanFilters.length; i++) {
                finalDomain.push("&"); // Agregar `"&"` antes de las condiciones
            }
        }
        finalDomain.push(...cleanFilters);

        console.log('✅ Dominio final estructurado:', finalDomain);

        // 🔹 **Aplicar el nuevo dominio**
        await this.env.searchModel.replaceDomain(finalDomain);

        popup.remove();
    }

    async _onFilterChange(event, fieldName) {
        const value = event.target.value.trim();
        if (value) {
            let domain = [[fieldName, "ilike", value]];
            console.log("🔍 Filtrando con Enter:", domain);
            await this.env.searchModel.splitAndAddDomain(domain);
        }
    }
}


class CustomListController extends ListController {
}

export const customListView = {
    ...listView,
    Controller: CustomListController,
    Renderer: CustomListRenderer,
};


registry.category("views").add("adaptative_filter", customListView);

patch(SearchModel.prototype, {
    async replaceDomain(domain) {
        console.log("🔄 Reemplazando filtros con:", domain);

        const groups = this._getGroups();
        for (const group of groups) {
            this.deactivateGroup(group.id);  // Desactivar grupos existentes de filtros
        }

        const tree = treeFromDomain(domain, {distributeNot: !this.isDebugMode});

        const trees = !tree.negate && tree.value === "&" ? tree.children : [tree];

        const promises = trees.map(async (tree) => {
            const description = await this.getDomainTreeDescription(this.resModel, tree);
            return {
                description,
                domain: domainFromTree(tree),
                invisible: "True",
                type: "filter",
            };
        });

        const preFilters = await Promise.all(promises);

        this.blockNotification = true;

        for (const preFilter of preFilters) {
            this.createNewFilters([preFilter]);
        }

        this.blockNotification = false;
        this._notify();
    }


})