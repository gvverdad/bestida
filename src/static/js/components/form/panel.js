import { LitElement, html, css } from 'lit'
import { TWStyles } from '../../../css/tw.js'

import store from "../../store"
import { buildField } from "./fieldbuilder"
import { CreateValidationSchema, ExtractFieldValidators, ActionOn, Cascade,
        ConvertToFormValues, CreateValidationContext,
        CreateFormValidator, ValidateFields } from "./formutils"
import { isNull, isNil, isArray, isEmpty, get, set } from "../../utils"


export class FormPanel extends LitElement {
    static styles = [
        css `
            :host{
                height: 100%;
                width: 100%;
                overflow: auto;
            }
        `,
        TWStyles
    ];

    static properties = {
        ownerId: { type: String },
        owner: { type: Object },
        mode: { type: String },
        activeStep: { type: Object },
        schemaFields: { type: Object },
        schemaPanels: { type: Object },
        program: { type: String },
        securityLevel: { type: Object },

        localData: { type: Boolean },
        autoDefault: { type: Boolean },
        formData: { type: Object },

        parentTable: { type: String },
        parentField: { type: String },
        parentRowId: { type: Number },
        parentRow: { type: Object },
        joinList: { type: Array },

        getGridSchemaHandler: { type: Function },
        getGridDataHandler: { type: Function },
        gridOptions: { type: Object },

        panel: { state: true },
        form_fields: { state: true },
    };

    static instanceCounter = 0;

    constructor() {
        super();
        this.instanceId = "FormPanel-" + (++FormPanel.instanceCounter).toString();

        this.handleFieldRegister = this.handleFieldRegister.bind(this);
        this.handleFieldUpdate = this.handleFieldUpdate.bind(this);
        this.handleFieldBlur = this.handleFieldBlur.bind(this);
        this.getGridData = this.getGridData.bind(this);

        this.activeStep = 0;
        this.currentActiveStep = 0;
        this.schemaFields = null;
        this.schemaPanels = null;
        this.program = null;

        this.mode = null;

        this.ownerId = null;
        this.owner = null;
        this.formData = {};
        this.autoDefault = false;
        this.localData = false;
        this.parentRow = null;
        this.validationSchema = null;
        this.validationList = [];

        this.panel = null;
        this.panel_fields = null;
        this.fieldNodes = {};
        this.errorFocused = false;
        this.formErrorFocused = false;
        this.errors = {};

        this.form_fields = [];

        this.getGridSchemaHandler = null;
        this.getGridDataHandler = null;
        this.gridOptions = null;

        this.securityLevel = {
            "runLevel": 999,
            "createLevel": 999,
            "updateLevel": 999,
            "deleteLevel": 999
        };

        this.addEventListener(`form-field-updated-${this.instanceId}`, this.handleFieldUpdate);
        this.addEventListener(`form-field-blur-${this.instanceId}`, this.handleFieldBlur);
        this.addEventListener(`form-field-register-${this.instanceId}`, this.handleFieldRegister);
    }

    connectedCallback() {
        super.connectedCallback();

        if(!isNull(this.schemaPanels)) {
            this.panel = this.schemaPanels[this.activeStep];
            this.panel_fields = this.schemaFields.filter(obj => obj.table === this.panel.table);
        }
    }

    firstUpdated() {
        if(!this.panel.use_list) {
            this.showForm();
        }
    }

    initForm() {
        this.validationSchema = null;
        this.validationList = [];
        this.fieldNodes = {};
        this.errors = {};
        this.errorFocused = false;
        this.formErrorFocused = false;
    }

    async showForm() {
        this.form_fields = [];
        this.currentActiveStep = this.activeStep;

        if(this.panel && this.panel_fields) {
            let index = 0;  // to determine autofocus
            this.initForm();

            for (const field of this.panel_fields) {
                if(field.modifiable) {
                    if(!field.autoDefault) field.autoDefault = this.autoDefault;
                    const node = buildField(field, index, this.formData, this.parentRow, this.mode);

                    index += 1;
                    node.ownerId = this.instanceId;
                    node.owner = this;

                    this.populateValidationList(field);
                    this.addFieldNode(node);

                    /*
                        The spread operator [...] takes all the elements from
                        the existing this.form_fields array and "spreads" them into a new array.
                        Updating the array immutably (by creating a new array)
                        ensures LitElement can detect changes and trigger a re-render.
                        Directly mutating this.form_fields (e.g., with push())
                        wouldn't necessarily notify LitElement that the array has changed

                        this.form_fields is reactive - form_fields: { state: true }
                        no need for this.requestUpdate();
                    */
                    this.form_fields = [...this.form_fields, node];

                    // wait until node is rendered
                    await this.waitRenderComplete(node);
                } else if(!isEmpty(field.join_list) && field.join_list[0][2] === this.parentTable) {
                    const data = get(this.formData, field.name, null);
                    if(isEmpty(data)) {
                        const obj = {};
                        // avoid cyclic data
                        Object.entries(this.parentRow).forEach(([key, value]) => {
                            if(key !== this.parentField) {
                                obj[key] = value;
                            }
                        });
                        set(this.formData, field.name, obj);
                    }
                }
            }
            this.finalizeForm();
        }
    }

    waitRenderComplete(node) {
        return new Promise((resolve) => {
            const onRenderComplete = (event) => {
                node.removeEventListener(`render-complete-${this.instanceId}`, onRenderComplete);
                resolve();
            };
            node.addEventListener(`render-complete-${this.instanceId}`, onRenderComplete);
        });
    }

    addFieldNode(node) {
        const fnode = {"node": node, "isLit": true};
        this.fieldNodes[node.name] = fnode;
        // pass up to form
        this.dispatchEvent(new CustomEvent(`form-node-register-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: { key: node.name,
                      node: fnode
                   }
            }));
    }

    populateValidationList(field) {
        const element = ExtractFieldValidators(field);
        if(element) {
            this.validationList.push(element);
        }
    }

    finalizeForm() {
        this.validationSchema = CreateValidationSchema(this.validationList);
        if(this.owner.formValidator) {
            this.validationSchema = CreateFormValidator(this.owner.formValidator,
                                                        this.fieldNodes,
                                                        this.validationSchema);
        }

        // Apply default ActionOn
        this.panel_fields.forEach(field => {
            if(field.name in this.fieldNodes) {
                const value = get(this.formData, field.name);
                ActionOn(this.fieldNodes, field,
                            isArray(value) ? value[0] : value);
            }
        });
    }

    handleFieldRegister(event) {
        // pass up to form
        this.dispatchEvent(new CustomEvent(`form-field-register-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: event.detail
        }));
    }

    handleFieldUpdate(event) {
        // field-update events from Children Lit Components
        const key = event.detail.key;
        const value = event.detail.value;

        set(this.formData, key, value);

        // pass up to form
        let sender = event.detail.sender ? event.detail.sender : [];
        sender.push(`${this.instanceId}.handleFieldUpdate`);
        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                key: key,
                value: value,
                sender: sender
                }
        }));

        // Action On/Cascade
        if(this.panel_fields) {
            const base_field = this.panel_fields.filter(obj => obj.name === key);
            if(base_field.length > 0) {
                ActionOn(this.fieldNodes, base_field[0],
                    isArray(value) ? value[0] : value);
                Cascade(this, base_field[0],
                        event.detail.record ? event.detail.record : value);
            }
        }
    }

    handleFieldBlur(event) {
        // pass up to form
        this.dispatchEvent(new CustomEvent(`form-field-blur-${this.ownerId}`, {
                    bubbles: true,
                    composed: true
        }));
    }

    async setFieldValue(name, value) {
        if(!(name in this.fieldNodes)) return false;

        set(this.formData, name, value);

        const node = this.fieldNodes[name].node;
        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: { key: name,
                              value: value,
                              type: node.type,
                              fieldType: node.fieldType,
                              record: null,
                              sender: [`${this.instanceId}.setFieldValue`]
                              }
        }));

        await node.setFieldValue(value);
    }

    // called by parent Form
    validate(force=false) {
        if(!force && this.panel.use_list) {
            const grid = this.shadowRoot.querySelector('ui-datatable');
            if(grid) return grid.validate();
            return true;
        }

        return ValidateFields(this);
    }
    // called by parent Form
    updateData() {
        // panel form updates the parent data on form input
        if(this.panel.use_list) {
            const grid = this.shadowRoot.querySelector('ui-datatable');
            if(grid) return grid.updateData(this.panel.id);
        }
    }
    // called by parent form
    focus() {
        Object.keys(this.fieldNodes).forEach(fieldName => {
            if(this.fieldNodes[fieldName].isLit) {
                this.fieldNodes[fieldName].node.focus();
            }
        });
    }

    getGridData(grid_columns, criteria, criteria_type, page, pagesize, selected_rows,
                        parent_table, parent_field, parent_row_id) {

        if(this.getGridDataHandler) {
           return this.getGridDataHandler(grid_columns, criteria, criteria_type, page,
                                    pagesize, selected_rows, parent_table, parent_field,
                                    parent_row_id);
        } else {
            const result = {};
            result.data = get(this.formData, this.panel.id, []);
            result.recordsTotal = result.data.length;

            return result;
        }
    }

    showTable(container) {
        let parent_row = this.formData;
        if(this.activeStep > 0) {
            if(!isNull(this.panel.field_list)) {
                const parents = this.panel.field_list.split(".");
                const parent = parents.slice(0, -1).join(".");
                parent_row = get(this.formData, parent, []);
            }
        }
        const row_id = parent_row.Id || 0;
        parent_row = JSON.stringify(parent_row).replace(/'/g, "&#39;"); // escape single quotes for JSON

        const program = `${this.program}.${this.panel.table}`;
        const join_list = JSON.stringify(this.panel.join_list);
        const sec_level = JSON.stringify(this.securityLevel);

        let grid_options = null;
        if(!isEmpty(this.gridOptions)) grid_options = JSON.stringify(this.gridOptions);

        container.innerHTML = `
            <ui-datatable
                owner-id="${this.ownerId}"
                grid-title="${this.panel.desc || this.panel.label}"
                db-table="${this.panel.table}"
                program="${program}"

                parent-table="${this.panel.parent || this.parentTable}"
                parent-field="${this.panel.field_list || this.parentField}"
                parent-row-id="${row_id}"

                security-level='${sec_level}'
                parent-row='${parent_row}'
                join-list='${join_list}'

                local-data
                active-next-button
                ${this.mode === "Delete" ? "" : "add-button"}
                ${this.mode === "Delete" ? "" : "copy-button"}
                ${this.mode === "Delete" ? "" : "update-button"}
                ${this.mode === "Delete" ? "" : "delete-button"}
                filter-button
                column-button
                download-button
                print-button
                ${grid_options ? `grid-options='${grid_options}'` : ""}
            ></ui-datatable>
        `;

        const createdElement = container.querySelector('ui-datatable');
        if(createdElement) {
            // additional properties that cannot be defined as string above
            if(!isEmpty(this.getGridSchemaHandler)) {
                createdElement.getGridSchemaHandler = this.getGridSchemaHandler;
            }
            createdElement.getGridDataHandler = this.getGridData;
            // TODO: remove formPanel
            createdElement.formPanel = this;
            createdElement.owner = this;
        }
    }

    updated() {
        if(this.panel.use_list) {
            const cont = this.shadowRoot.querySelector("[data-panelGridContainer]");
            if(cont) {
                // use removeChild loop instead of innerHTML = "" to properly
                // remove litelements
                while (cont.firstChild) {
                    cont.removeChild(cont.firstChild);
                }
                this.showTable(cont);
            }
        } else if(this.activeStep !== this.currentActiveStep) {
            this.showForm();
        }
    }

    shouldUpdate(changedProperties) {
        // check if can render
        if(!isNull(this.panel)) {
            if(this.schemaPanels[this.activeStep].table !== this.panel.table) {
                this.panel = this.schemaPanels[this.activeStep];
                this.panel_fields = this.schemaFields.filter(obj => obj.table === this.panel.table);
            }
            return true;
        } else return false;
    }

    getData() {
        if(this.owner) return this.owner.getData();

        return this.formData();
    }

    render() {
        if(this.panel.use_list) {
            return html`
                <div class="flex flex-col justify-center items-center w-full h-full"
                    data-panelGridContainer >
                </div>
            `;
        } else {
            return html`
                <form
                    class="card bg-base-100 shadow-xl group w-full"
                    novalidate
                    autocomplete="off"
                >
                    <div class="card-body">
                        <div class="form-control">
                            ${this.form_fields.map((field) => html`${field}`)}
                        </div>
                    </div>
                </form>
            `;
        }
    }
}

customElements.define("form-panel", FormPanel)
