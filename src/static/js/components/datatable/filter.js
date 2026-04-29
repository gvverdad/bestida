import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../css/tw.js'

import "../../../icons/x.js"
import { buildField } from "../form/fieldbuilder"
import { isEmpty, isNull, set, serializeTemporal, isArray } from "../../utils"

class FilterFields extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static instanceCounter = 0;

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        gridColumns: { attribute: "filter-columns", type: Object }
    };

    constructor() {
        super();
        this.instanceId = (++FilterFields.instanceCounter).toString();

        this.onSelect = this.onSelect.bind(this);

        this.gridColumns = null;
    }

     connectedCallback() {
        super.connectedCallback();

        this.instanceId = `FilterFields-${this.datatableId}-${this.instanceId}`;
    }

    onSelect(event) {
        // this is a bubbled event - we are interested in the li click
        const li = event.target.closest("li");
        if(li === null) return false;

        this.dispatchEvent(new CustomEvent(`fields-select-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: {
                value: li.dataset.key
            }
        }));

        const dialog = this.shadowRoot.querySelector("ui-dialog");
        dialog.closeModal();
    }

    show() {
        const dialog = this.shadowRoot.querySelector("ui-dialog");
        dialog.showModal();
    }

    render() {
        let columns = this.gridColumns === null ? [] : this.gridColumns;
        columns = columns.filter(obj => obj.searchable);

        return html`
            <ui-dialog owner-id="${this.instanceId}" >
                <caption class="caption-top font-semibold">
                    Select Filter Field
                </caption>
                <ul tabindex="0" @click="${this.onSelect}"
                    class="block dropdown-content z-[50] menu p-2 shadow bg-base-200 text-base-content rounded-box w-max">
                    ${columns.map(column =>
                        html`
                            <li data-key="${column.name}"><span>${column.label}</span></li>
                        `
                    )}
                </ul>
            </ui-dialog>
        `;
    }
}
customElements.define("filter-fields", FilterFields)

class FilterOps extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        dataType: { attribute: "data-type", type: String },
        index: { attribute: "index", type: Number },
        value: { attribute: "default-value", type: Number }
    };

    constructor() {
        super();
        this.onOpSelect = this.onOpSelect.bind(this);

        this.dataType = null;
        this.index = null;
        this.value = 0;

        this.op_str = [
            {"key":0, "value":"EQUALS"},
            {"key":1, "value":"NOT EQUALS"},
            {"key":2, "value":"LESS THAN"},
            {"key":3, "value":"LESS THAN OR EQUALS"},
            {"key":4, "value":"GREATER THAN"},
            {"key":5, "value":"GREATER THAN OR EQUALS"},
            {"key":6, "value":"BETWEEN"},
            {"key":7, "value":"NOT BETWEEN"},
            {"key":8, "value":"IN LIST"},
            {"key":9, "value":"NOT IN LIST"},
            {"key":10, "value":"BEGINS"},
            {"key":11, "value":"NOT BEGINS"},
            {"key":12, "value":"ENDS"},
            {"key":13, "value":"NOT ENDS"},
            {"key":14, "value":"CONTAINS"},
            {"key":15, "value":"NOT CONTAINS"},
            {"key":16, "value":"EMPTY"},
            {"key":17, "value":"NOT EMPTY"},
        ];

        this.op_number = [
            {"key":0, "value":"EQUALS"},
            {"key":1, "value":"NOT EQUALS"},
            {"key":2, "value":"LESS THAN"},
            {"key":3, "value":"LESS THAN OR EQUALS"},
            {"key":4, "value":"GREATER THAN"},
            {"key":5, "value":"GREATER THAN OR EQUALS"},
            {"key":6, "value":"BETWEEN"},
            {"key":7, "value":"NOT BETWEEN"},
            {"key":8, "value":"IN LIST"},
            {"key":9, "value":"NOT IN LIST"},
            {"key":16, "value":"EMPTY"},
            {"key":17, "value":"NOT EMPTY"},
        ];

        this.op_bool = [
            {"key":0, "value":"EQUALS"},
            {"key":1, "value":"NOT EQUALS"},
            {"key":16, "value":"EMPTY"},
            {"key":17, "value":"NOT EMPTY"},
        ];

    }

    onOpSelect(event) {
        // events bubbles up the hierarchy not sideways to siblings
        // hence FilterValue cannot catch ops-select event
        this.dispatchEvent(new CustomEvent(`ops-select-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: {
                value: parseInt(event.target.value),
                index: this.index
            }
        }));
    }

    render() {

        let op = [];
        switch(this.dataType) {
            case "Integer":
            case "BigInteger":
            case "Numeric":
            case "Date":
            case "Time":
            case "DateTime":
                op = this.op_number;
                break;
            case "Boolean":
                op = this.op_bool;
                break;
            default:
                op = this.op_str;
        }

        return html`
            <select @change="${this.onOpSelect}"
                class="select select-ghost w-fit"
            >
                ${op.map((ele) =>
                    html `
                        <option value="${ele.key}"
                            ?selected="${ele.key === this.value}">
                            ${ele.value}
                        </option>
                    `
                )}
            </select>
        `;
    }
}
customElements.define("filter-ops", FilterOps)


class FilterValue extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static instanceCounter = 0;

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        dataType: { attribute: "data-type", type: String },
        index: { attribute: "index", type: Number },
        ops: { attribute: "ops", type: Number },
        defaultValue: { attribute: "default-value", type: Object },
        schema: { type: Object },

        OK2Render: { state: true }
    };

    constructor() {
        super();
        this.instanceId = "FilterValue-" + (++FilterValue.instanceCounter).toString();

        this.handleOpsSelect = this.handleOpsSelect.bind(this);
        this.handleFieldUpdate = this.handleFieldUpdate.bind(this);

        this.dataType = "String";
        this.index = null;
        this.value = null;
        this.defaultValue = null;
        this.ops = 0;
        this.schema = null;
        this.component = null;
        this.OK2Render = false;

        // cannot use eventListener to catch ops-select CustomEvent
        // events bubbles up the hierarchy not sideways to siblings
        this.addEventListener(`form-field-updated-${this.instanceId}`, this.handleFieldUpdate);
    }

     connectedCallback() {
        super.connectedCallback();

        this.value = this.defaultValue;

        this.createComponent();
        this.OK2Render = true;
    }

    handleOpsSelect(index, value) {
        // ops-select event called by DatatableFilter
        if(index !== this.index) return false;
        this.ops = value;
        this.value = null;

        this.OK2Render = false;
        this.createComponent();
        this.OK2Render = true;
    }

    handleValueChange(value) {
        this.dispatchEvent(new CustomEvent(`value-update-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: {
                value: value,
                index: this.index
            }
        }));
    }

    handleFieldUpdate(event) {
        // field-update events from Children Lit Components
        const type = event.detail.fieldType;
        let value = event.detail.value;

        if(type && value &&
            ["date","datetime","time"].includes(type.toLowerCase())) {
            // serialize for json transport
            if(isArray(value)) {
                this.value = [];
                value.forEach(val => {
                    this.value.push(serializeTemporal(val, type));
                });
            } else this.value = serializeTemporal(value, type);
        } else this.value = value;

        this.handleValueChange(this.value);
    }

    createComponent() {
        this.component = null;
        /**** this.ops
                0=EQUALS
                1=NOT EQUALS
                2=LESS THAN
                3=LESS THAN or EQUALS
                4=GREATER THAN
                5=GREATER THAN or EQUALS
                6=BETWEEN
                7=NOT BETWEEN
                8=IN LIST
                9=NOT IN LIST
                10=BEGINS
                11=NOT BEGINS
                12=ENDS
                13=NOT ENDS
                14=CONTAINS
                15=NOT CONTAINS
                16=EMPTY
                17=NOT EMPTY
        ****/
        if(this.ops < 16) {
            const field = structuredClone(this.schema);    // deep copy
            const label = field.label;
            field.label = null;
            field.required = true;  // remove field x button (clear)
            field.range = false;
            field.multiple = false;

            if(["date","datetime","time"].includes(field.type.toLowerCase())) {
                field.required = false;  // field x button (clear)
                field.dateMode = "single";
                if(this.ops > 7) field.dateMode = "multiple";  // LIST
                else if(this.ops > 5) field.dateMode = "range";  // BETWEEN
            } else if(this.ops > 9) {
                // BEGINS, ENDS, CONTAINS
                field.type = "String";
            } else if(field.selectTable) {
                field.type = "Select";
                if(this.ops > 7) {
                    // LIST
                    field.use_list = true;  // multiple select
                }
            } else if(this.ops > 7) {
                // LIST
                if(["integer","biginteger,numeric"].includes(field.type.toLowerCase())) {
                    field.type = "String";
                }
            }
            if(this.ops > 5 && this.ops < 8) {
                // BETWEEN
                field.range = true;
            }

            // focus
            let index = this.index;
            if(isNull(this.value) || isEmpty(this.value)) index = 0;

            if(this.dataType === "Boolean") {
                if(isNull(this.value)) {
                    this.value = false;
                    this.handleValueChange(this.value);
                }
            }
            const formData = {};
            set(formData, field.name, this.value);

            this.component = buildField(field, index, formData, null, "Update");
            this.component.ownerId = this.instanceId;

            if(this.ops > 7 && this.ops < 10) {
                // LIST
                if(field.type !== "Select")
                    this.component.hint = `Comma Separated List of ${label}`;
            }
        }
    }

    shouldUpdate() {
        return this.OK2Render;
    }

    render() {
        return html`
            ${this.component
            ? html`${this.component}`
            : nothing }
        `;
    }
}
customElements.define("filter-value", FilterValue)


class DatatableFilter extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        gridColumns: { attribute: "grid-columns", type: Object },
        criteria: { type: Object },
        criteriaType: { attribute: "criteria-type", type: Number }
    };

    constructor() {
        super();
        this.onAddFilter = this.onAddFilter.bind(this);
        this.onApplyFilter = this.onApplyFilter.bind(this);
        this.onRemoveCriteria = this.onRemoveCriteria.bind(this);
        this.handleOpsSelect = this.handleOpsSelect.bind(this);
        this.handleValueUpdate = this.handleValueUpdate.bind(this);
        this.handleFieldSelect = this.handleFieldSelect.bind(this);
        this.onTypeSelect = this.onTypeSelect.bind(this);

        this.gridColumns = null;
        this.fields = null;

        this.criteria = [];
        this.criteriaType = 0; // ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3
    }

     connectedCallback() {
        super.connectedCallback();

        this.addEventListener(`fields-select-${this.datatableId}`, this.handleFieldSelect);
        this.addEventListener(`ops-select-${this.datatableId}`, this.handleOpsSelect);
        this.addEventListener(`value-update-${this.datatableId}`, this.handleValueUpdate);
    }

    disconnectedCallback() {
        super.disconnectedCallback();
        this.removeEventListener(`fields-select-${this.datatableId}`, this.handleFieldSelect);
        this.removeEventListener(`ops-select-${this.datatableId}`, this.handleOpsSelect);
        this.removeEventListener(`value-update-${this.datatableId}`, this.handleValueUpdate);
    }

    firstUpdated() {
        this.fields = this.shadowRoot.querySelector("filter-fields");
        this.collapse = this.shadowRoot.querySelector(".collapse");

        if(this.criteria.length > 0) {
            this.collapse.classList.add("collapse-open");
            this.collapse.classList.remove("collapse-close");
        }
    }

    handleFieldSelect(event) {
        const index = this.gridColumns.findIndex(obj => obj.name === event.detail.value);

        this.criteria.push({
            index: index,
            label: this.gridColumns[index].label,
            type: this.gridColumns[index].type,
            field: this.gridColumns[index].name,
            schema: this.gridColumns[index],
            op: 0,
            value: null
        });
        if (!this.collapse.classList.contains("collapse-open")) {
            this.collapse.classList.add("collapse-open");
            this.collapse.classList.remove("collapse-close");
        }
        this.requestUpdate(); // force render
    }

    handleOpsSelect(event) {
        this.criteria[event.detail.index].op = event.detail.value;
        // FilterValue cannot use eventListener to catch ops-select CustomEvent
        // events bubbles up the hierarchy not sideways to siblings
        const child_value = this.shadowRoot.querySelector(`filter-value[index="${event.detail.index}"]`);
        if(child_value) child_value.handleOpsSelect(event.detail.index, event.detail.value);
    }

    handleValueUpdate(event) {
        this.criteria[event.detail.index].value = event.detail.value;
    }

    onRemoveCriteria(event) {
        const button = event.target.closest("button");
        if(button === null) return false;

        const index = parseInt(button.dataset.key);
        this.criteria.splice(index, 1);

        this.requestUpdate(); // force render
    }

    onTypeSelect(event) {
        this.criteriaType = parseInt(event.target.value);
    }

    onAddFilter(event) {
        this.fields.gridColumns = this.gridColumns;
        this.fields.show();
    }

    onApplyFilter(event) {
        this.dispatchEvent(new CustomEvent(`grid-apply-filter-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: {
                criteria: this.criteria,
                type: this.criteriaType
            }
        }));
    }

    render() {
        return html`
            <div class="card bg-base-100 shadow-xl">
                <div class="card-body">
                    <div class="flex w-1/3 justify-between items-center">
                        <button class="btn btn-primary"
                            @click="${this.onAddFilter}"
                        >Add Filter</button>
                        <label class="cursor-pointer label font-medium">
                            <select @change="${this.onTypeSelect}"
                                class="select select-ghost w-fit"
                                style="padding-right: 10px;"
                            >
                                <option value="0" ?selected="${this.criteriaType === 0}">ALL</option>
                                <option value="1" ?selected="${this.criteriaType === 1}">ANY</option>
                                <option value="2" ?selected="${this.criteriaType === 2}">NONE</option>
                                <option value="3" ?selected="${this.criteriaType === 3}">NOT ALL</option>
                            </select>
                            <span class="label-text pl-2">of the following criteria are met</span>
                        </label>
                    </div>
                    <div tabindex="0" class="collapse bg-base-100">
                        <div class="collapse-content">
                            <table class="table table-pin-rows table-auto">
                                <thead>
                                    <tr class="bg-base-300 h-10">
                                        <th></th>
                                        <th class="align-middle text-sm font-semibold">Field</th>
                                        <th class="align-middle text-sm font-semibold">Operation</th>
                                        <th class="align-middle text-sm font-semibold">Value</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    ${this.criteria.map((crit, index) =>
                                        html`
                                            <tr class="hover h-10 bg-base-100 text-content">
                                                <td><div class="tooltip tooltip-bottom" data-tip="Remove Filter">
                                                    <button @click="${this.onRemoveCriteria}"
                                                        data-key="${index}" class="btn btn-ghost rounded-full"
                                                        style="padding: 5px; height: inherit; min-height: inherit;">
                                                        <icon-x class="w-5 h-5"></icon-x>
                                                    </button>
                                                </div></td>
                                                <td>${crit.label}</td>
                                                <td><filter-ops
                                                    datatable-id="${this.datatableId}"
                                                    data-type="${crit.type}"
                                                    index="${index}"
                                                    default-value="${crit.op}"
                                                ></filter-ops></td>
                                                <td><filter-value
                                                    datatable-id="${this.datatableId}"
                                                    data-type="${crit.type}"
                                                    index="${index}"
                                                    ops="${crit.op}"
                                                    default-value='${JSON.stringify(crit.value)}'
                                                    schema='${JSON.stringify(crit.schema)}'
                                                ></filter-value></td>
                                            </tr>
                                        `
                                    )}
                                </tbody>
                            </table>
                        </div>
                    </div>
                    <div class="card-actions justify-end">
                        <button
                            @click="${this.onApplyFilter}"
                            class="btn btn-primary"
                        >Apply Filter</button>
                    </div>
                </div>
            </div>
            <filter-fields
                datatable-id="${this.datatableId}"
            ></filter-fields>
        `;
    }
}

customElements.define("datatable-filter", DatatableFilter)
