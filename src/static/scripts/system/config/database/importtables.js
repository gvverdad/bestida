import { LitElement, html, css } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../../../css/tw.js'
import * as XLSX from 'xlsx';

import breadcrumbs from "../../../../js/breadcrumb"
import { isNil, isEmpty, isArray, get, set } from "../../../../js/utils"

class ImportTables extends LitElement {
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

    static instanceCounter = 0;

    static properties = {
        // populated by Script Driver
        title: { type: String },
        ownerId: { type: String },
        scriptId: { type: String},
        program: { type: String},

        activeStep: { state: true },
        disableNextButton: { state: true },
        nextText: { state: true },
    }

    constructor() {
        super();
        this.instanceId = "ImportTables-" + (++ImportTables.instanceCounter).toString();

        this.handleNextButtonDisable = this.handleNextButtonDisable.bind(this);
        this.handleStepMode = this.handleStepMode.bind(this);
        this.handleUpdateData = this.handleUpdateData.bind(this);

        this.buildMapPage = this.buildMapPage.bind(this);
        this.getMapFormSchema = this.getMapFormSchema.bind(this);
        this.getMapFormData = this.getMapFormData.bind(this);
        this.getMapGridSchema = this.getMapGridSchema.bind(this);
        this.getMapGridData = this.getMapGridData.bind(this);
        this.mapFormValidator = this.mapFormValidator.bind(this);

        this.onCancel = this.onCancel.bind(this);
        this.onBack = this.onBack.bind(this);
        this.onNext = this.onNext.bind(this);
        this.onStep = this.onStep.bind(this);

        this.title = null;

        this.steps = ["Rulesets", "Ruleset", "Maps", "Duplicates", "Task"];
        this.activeStep = 0;
        this.watermark = 0;
        this.pageType = null;
        this.program = null;

        this.data = {
            Title: null,
            Params: {
                maps: {
                    data: {},
                    fields: [] },
                dups: {}
            }
        };
        this.rowId = null;
        this.mode = null; // Create,Update,Delete

        this.disableNextButton = false;

        this.cancelText = "Cancel";
        this.backText = "Back";
        this.nextText = "Next";
        this.nextOrigText = "Next";
        this.submitText = "Submit";

        this.mapGridFields = [];
        this.mapGridTables = [];
        this.mapGridData = [];
        this.mapFormFields = [];
        this.mapFormPanels = [];
        this.mapFormData = {};
        this.tableFields = [];

        this.file_columns = [];
        this.table = null;
        this.numberOfTables = 0;

        this.runscript = "tasks.system.import.importtables.ImportTables";

        this.addEventListener(`submit-button-disable-${this.instanceId}`, this.handleNextButtonDisable);
        this.addEventListener(`step-mode-${this.instanceId}`, this.handleStepMode);
        this.addEventListener(`grid-select-row-${this.instanceId}`, this.handleUpdateData);
        this.addEventListener(`form-field-updated-${this.instanceId}`, this.handleUpdateData);
    }

    async connectedCallback() {
        super.connectedCallback();
    }


    onCancel(event) {
        event.preventDefault();

        breadcrumbs.closePage();
    }

    onBack(event) {
        event.preventDefault();

        this.activeStep -= 1;
    }

    onNext(event) {
        event.preventDefault();

        const page = this.shadowRoot.querySelector(this.pageType);
        if(!page.handleStepperNext(event, "", this.data, this.activeStep, this.steps.length-1))
            return false;

        if(this.activeStep === (this.steps.length-1))  {
            return page.handleSubmit();
        } else {
            this.activeStep += 1;
            this.watermark = Math.max(this.watermark, this.activeStep);
        }
    }

    onStep(step) {
        if(step <= this.watermark) {
            if(step > this.activeStep && this.disableNextButton) {
                return false;
            }

            this.activeStep = step;
        }
    }

    handleNextButtonDisable(event) {
        this.disableNextButton = event.detail.value;
        if(!isNil(event.detail.buttonText)) {
            this.nextText = event.detail.buttonText;
        } else this.nextText = this.nextOrigText;
    }

    handleStepMode(event) {
        this.mode = event.detail.mode;
    }

    handleUpdateData(event) {
        if(!isEmpty(event.detail.key)) {
            // form field
            set(this.data, event.detail.key, event.detail.value);
        } else {
            // grid row
            this.data = event.detail.value ? event.detail.value :
                        {
                            Title: null,
                            Params: {
                                maps: {
                                    data: {},
                                    fields: [] },
                                dups: {}
                            }
                        };
            this.rowId = !isNil(this.data.Id) ? this.data.Id : 0;
        }
    }

    async buildMapPage(event) {
        const dummy_table = "ImportTablesMap";
        const currentTable = get(this.data, "Params.table", null);
        if(currentTable && this.table && currentTable !== this.table) {
            set(this.data, "Params.maps.data", {});
            set(this.data, "Params.dups", {});
        }
        this.table = currentTable;

        this.mapFormPanels = [
            {
                'table': dummy_table,
                "desc": "Import Table Maps",
                "use_list": true,
                "id": dummy_table
            }
        ];
        this.mapGridTables = [{
            "table": dummy_table,
        }];
        this.mapGridFields = [
            {
                "name": "field_label",
                "field_name": "field_label",
                "label": "Field",
                "column_label": "Field",
                "table": dummy_table,
                "type": "String",
                "length": 64,
                "decimals": 0,
                "join": false,
                "join_list": null,
                "use_list": false,
                "default": null,
                "validValuesKey": null,
                "validValues": null,
                "enums": null,
                "enum_getter": null,
                "actionOn": null,
                "validator": null,
                "min": null,
                "max": null,
                "listFormat": false,
                "listMin": null,
                "listMax": null,
                "required": false,
                "requiredIf": null,
                "selectId": "Id",
                "selectKey": null,
                "selectTable": null,
                "selectObject": null,
                "selectFormat": null,
                "selectCascade": null,
                "child_name": null,
                "modifiable": false,
                "sortable": false,
                "visible": true,
                "cell_function": null,
                "options": {
                    "sort": false,
                    "sortDirection": "none",
                    "display": true,
                    "modifiable": false
                }
            }, {
                "name": "field_action",
                "field_name": "field_action",
                "label": "Action",
                "column_label": "Action",
                "table": dummy_table,
                "type": "String",
                "length": 16,
                "decimals": 0,
                "join": false,
                "join_list": null,
                "use_list": false,
                "default": null,
                "validValuesKey": null,
                "validValues": null,
                "enums": null,
                "enum_getter": null,
                "actionOn": null,
                "validator": null,
                "min": null,
                "max": null,
                "listFormat": false,
                "listMin": null,
                "listMax": null,
                "required": false,
                "requiredIf": null,
                "selectId": "Id",
                "selectKey": null,
                "selectTable": null,
                "selectObject": null,
                "selectFormat": null,
                "selectCascade": null,
                "child_name": null,
                "modifiable": false,
                "sortable": false,
                "visible": true,
                "cell_function": null,
                "options": {
                    "sort": false,
                    "sortDirection": "none",
                    "display": true,
                    "modifiable": true
                }
            }, {
                "name": "field_value",
                "field_name": "field_value",
                "label": "Value",
                "column_label": "Value",
                "table": dummy_table,
                "type": "String",
                "length": 128,
                "decimals": 0,
                "join": false,
                "join_list": null,
                "use_list": false,
                "default": null,
                "validValuesKey": null,
                "validValues": null,
                "enums": null,
                "enum_getter": null,
                "actionOn": null,
                "validator": null,
                "min": null,
                "max": null,
                "listFormat": false,
                "listMin": null,
                "listMax": null,
                "required": false,
                "requiredIf": null,
                "selectId": "Id",
                "selectKey": null,
                "selectTable": null,
                "selectObject": null,
                "selectFormat": null,
                "selectCascade": null,
                "child_name": null,
                "modifiable": false,
                "sortable": false,
                "visible": true,
                "cell_function": null,
                "options": {
                    "sort": false,
                    "sortDirection": "none",
                    "display": true,
                    "modifiable": true
                },
                "colspan": 2
            }
        ];

        this.file_columns = [];
        if(!isEmpty(this.data.Params.header)) {
            const data = new Uint8Array(event.target.result);
            const workbook = XLSX.read(data, {type: 'array'});
            const first_sheet = workbook.SheetNames[0];
            const row_number = parseInt(this.data.Params.header);
            const header_row = row_number > 0 ? row_number : 1;
            const sheet_rows = XLSX.utils.sheet_to_json(workbook.Sheets[first_sheet],{
                header: header_row
            });
            sheet_rows[header_row-1].forEach((ele, idx) => {
                this.file_columns.push([idx+1, idx+1 + ": " + ele]);
            });
        }

        this.mapFormFields = [];
        this.mapFormData = {};
        this.tableFields = [];
        this.mapGridData = [];

        let col_idx = 0;
        let rows = 0;

        this.currentLabel = null;
        this.numberOfTables = 0;

        const tableSchema = await api.GET("/tableSchema/" + this.data.Params.table, null);
        set(this.data, "Params.tableSchema", tableSchema);
        if(!isNil(tableSchema.componentOf)) {
            const componentOf = tableSchema.componentOf;

            const data = await api.GET("/formSchema/" + componentOf.table, null);
            const schema = data.form_fields.filter(obj =>
                                      componentOf.key.includes(obj.field_name));
            schema.forEach((ele) => {
                this.populate_fields(dummy_table, ele, rows, col_idx,
                    data.form_panels);
                rows++;
            });
        }

        await api.GET("/formSchema/" + this.data.Params.table, null)
            .then(data => {
                data.form_fields.forEach((ele) => {
                    this.populate_fields(dummy_table, ele, rows, col_idx,
                        data.form_panels);
                    rows++;
                });
                this.numberOfTables = data.form_panels.length;
        });
        //set(this.data, "Params.maps.fields", this.mapFormFields);
        set(this.data, "Params.maps.fields", this.tableFields);
    }

    populate_fields(dummy_table, ele, row_idx, col_idx, panels) {

        let name = `Params.maps.data.field_action_${row_idx}`;
        let default_val = get(this.data, name, "NoAction");
        set(this.mapFormData, name, default_val);
        const action_idx = this.mapFormFields.push({
            "name": name,
            //"label": "Action",
            "table": dummy_table,
            "field_name": "field_action",
            "type": "Enum",
            "length": 16,
            "decimals": 0,
            "join": false,
            "join_list": null,
            "use_list": false,
            "default": default_val,
            "validValuesKey": null,
            "validValues": null,
            "enums": [
                ["NoAction","No Action"],
                ["Column","Import File Column"],
                ["Constant","Constant"]
            ],
            "enum_getter": null,
            "actionOn": {
                "baseFieldName": `Params.maps.data.field_action_${row_idx}`,
                "NoAction": {
                    "onFields": [],
                    "offFields": [
                        `Params.maps.data.field_value_column_${row_idx}`,
                        `Params.maps.data.field_value_constant_${row_idx}`
                    ]
                },
                "Column": {
                    "onFields": [
                        `Params.maps.data.field_value_column_${row_idx}`
                    ],
                    "offFields": [
                        `Params.maps.data.field_value_constant_${row_idx}`
                    ]
                },
                "Constant": {
                    "onFields": [
                        `Params.maps.data.field_value_constant_${row_idx}`
                    ],
                    "offFields": [
                        `Params.maps.data.field_value_column_${row_idx}`
                    ]
                }
            },
            "validator": null,
            "min": null,
            "max": null,
            "listFormat": false,
            "listMin": null,
            "listMax": null,
            "required": true,
            "requiredIf": null,
            "selectId": "Id",
            "selectKey": null,
            "selectTable": null,
            "selectObject": null,
            "selectFormat": null,
            "selectCascade": null,
            "id": row_idx,
            "seq": col_idx++,
            "modifiable": true
        });

        name = `Params.maps.data.field_value_column_${row_idx}`;
        default_val = get(this.data, name, "");
        set(this.mapFormData, name, default_val);
        const value_column_idx = this.mapFormFields.push({
            "name": name,
            "table": dummy_table,
            "field_name": "field_value_column",
            "type": "Enum",
            "length": 8,
            "decimals": 0,
            "join": false,
            "join_list": null,
            "use_list": false,
            "default": default_val,
            "validValuesKey": null,
            "validValues": null,
            "enums": this.file_columns,
            "enum_getter": null,
            "actionOn": null,
            "validator": null,
            "min": null,
            "max": null,
            "listFormat": false,
            "listMin": null,
            "listMax": null,
            "required": true,
            "requiredIf": `Params.maps.data.field_action_${row_idx} == "Column"`,
            "selectId": "Id",
            "selectKey": null,
            "selectTable": null,
            "selectObject": null,
            "selectFormat": null,
            "selectCascade": null,
            "id": row_idx,
            "seq": col_idx++,
            "modifiable": true
        });

        name = `Params.maps.data.field_value_constant_${row_idx}`;
        default_val = get(this.data, name, ele.default || "");
        set(this.mapFormData, name, default_val);
        const value_constant_idx = this.mapFormFields.push({
            "name": name,
            "table": dummy_table,
            "field_name": "field_value_constant",
            "type": ele.selectTable ? "Select" : ele.type,
            "length": ele.length,
            "decimals": ele.decimals,
            "join": ele.join,
            "join_list": ele.join_list,
            "use_list": ele.use_list,
            "default": default_val,
            "validValuesKey": ele.validValuesKey,
            "validValues": ele.validValues,
            "enums": ele.enums,
            "enum_getter": ele.enum_getter,
            "actionOn": ele.actionOn,
            "validator": ele.validator,
            "case": ele.case,
            "min": ele.min,
            "max": ele.max,
            "listFormat": ele.listFormat,
            "listMin": ele.listMin,
            "listMax": ele.listMax,
            "required": true,
            "requiredIf": `Params.maps.data.field_action_${row_idx} == "Constant"`,
            "selectId": ele.selectId,
            "selectKey": ele.selectKey,
            "selectTable": ele.selectTable,
            "selectObject": ele.selectObject,
            "selectFormat": ele.selectFormat,
            "selectCascade": ele.selectCascade,
            "id": row_idx,
            "seq": col_idx++,
            "modifiable": true
        });
console.log("importtables.populate_fields:", ele, panels);
        const panel = panels.find(pane => pane.table === ele.table);
        let label = null;
        if(panel) {
            label = panel.label || panel.desc;
            this.currentLabel = label;
        } else {
            label = `${this.currentLabel} - ${ele.table}`;
        }

        this.mapGridData.push({
            "Id": row_idx,
            "table_name": label,
            "field_name": ele.name,
            "field_label": ele.label,
            "field_action": this.mapFormFields[action_idx-1],
            "field_value": [this.mapFormFields[value_column_idx-1],
                            this.mapFormFields[value_constant_idx-1]]
        });

        this.tableFields.push({
            'name': ele.name,
            'label': ele.label,
            'table': ele.table,
            'type': ele.type,
            'join_list': ele.join_list,
            'select_key': ele.selectKey,
            'select_field': ele.selectField
        });
    }

    getMapFormSchema() {
        if(!isEmpty(this.data.Params.maps.data)) {
            // prev page event
            this.mapFormFields.forEach(field => {
                const value = get(this.data, field.name, "");
                if(isArray(value)) field.default = value[0];
                else field.default = value;
            });
        }
        return {form_fields: this.mapFormFields, form_panels: this.mapFormPanels};
    }

    getMapFormData() {
        if(!isEmpty(this.data.Params.maps.data)) {
            // prev page event
            this.mapFormFields.forEach(field => {
                const value = get(this.data, field.name, "");
                set(this.mapFormData, field.name, value);
            });
        }
        return {data: this.mapFormData};
    }

    async getMapGridSchema() {
        return {grid_fields: this.mapGridFields, grid_tables: this.mapGridTables};
    }

    async getMapGridData() {
        return {data: this.mapGridData};
    }

    mapFormValidator(fieldNodes, val_obj) {
        let fields = [];
        Object.keys(fieldNodes).forEach(key => {
            if(key.startsWith("Params.maps.data.field_action")) {
                fields.push(key);
            }
        });
        if(fields.length > 0) {
            if(isEmpty(val_obj)) {
                val_obj = Yup.object();
            }
            val_obj = val_obj.test(
                "import-tables-map-form-validator",
                'At least 1 line requires a non "No Action" Action',
                function(values) {
                    return fields.some(field => {
                        const value = get(values, field, null);
                        if(value) {
                            return value[0] !== "NoAction";
                        }
                        return false;
                    });
                }
            );
        }
        return val_obj;
    }

    renderStep() {
        let program = this.program;
        switch(this.activeStep) {
            case 0:
                this.pageType = "ui-datatable";
                program = `${program}.Rulesets`;
                return html`
                    <ui-datatable
                        owner-id="${this.instanceId}"
                        grid-title="Rulesets"
                        db-table="Rulesets"
                        program="${program}"
                        get-schema-url="/importtablesgridschema"
                        post-data-url="/importtablesrulesets"
                        select-row
                        form-mode
                        next-button-text="New"
                        next-button-select-text="Update"
                        active-next-button
                        delete-button
                        filter-button
                        column-button
                        refresh-button
                        download-button
                        print-button
                    ></ui-datatable>
                `;
            case 1:
                this.pageType = "ui-form";
                program = `${program}.Ruleset`;
                return html`
                    <ui-form
                        owner-id="${this.instanceId}"
                        mode="${this.mode}"
                        program="${program}"
                        form-title="Import Tables Ruleset"
                    >
                        <ui-input
                            label="Title"
                            name="Title"
                            type="text"
                            value="${get(this.data, 'Title', null)}"
                            required="Title is a Required Field"
                            autofocus
                        ></ui-input>
                        <ui-combobox label="Table"
                            name="Params.table"
                            value="${get(this.data, 'Params.table', null)}"
                            required="Table is a Required Field"
                            enum-getter="getAppTablesList"
                        ></ui-combobox>
                        <ui-input
                            label="Update Level"
                            name="Params.level"
                            type="number"
                            value="${get(this.data, 'Params.level', '1')}"
                            required="Update Level is a Required Field"
                            min="1"
                        ></ui-input>
                        <ui-input
                            label="Input File Header Row Number"
                            name="Params.header"
                            type="number"
                            value="${get(this.data, 'Params.header', null)}"
                            min="0"
                            max="5"
                        ></ui-input>
                        <ui-input
                            label="Input File"
                            name="Params.file"
                            type="file"
                            required="Input File is a Required Field"
                            accept=".csv,.tsv,.csvz,.tsvz,.xls,.xlsx,.xlsm,.ods"
                            .fileReaderOnLoadHandler="${this.buildMapPage}"
                        ></ui-input>
                   </ui-form>
                `;
            case 2:
                this.pageType = "ui-form";
                program = `${program}.Maps`;
                const page2Title = `Import Tables Maps - ${get(this.data, "Params.table", null)}`;
                const grid_options = {
                    toolbar: false,
                    footer: false
                };
                if(this.numberOfTables > 1) grid_options["sectionHeader"] = "table_name"; // this.mapGridData
                return html`
                    <ui-form
                        owner-id="${this.instanceId}"
                        mode="${this.mode}"
                        program="${program}"
                        form-title="${page2Title}"
                        db-table="Rulesets"  // dummy to force getSchema
                        row-id="9999"   // dummy to force getData

                        .getFormDataHandler="${this.getMapFormData}"
                        .getFormSchemaHandler="${this.getMapFormSchema}"
                        .formValidator="${this.mapFormValidator}"

                        .getGridDataHandler="${this.getMapGridData}"
                        .getGridSchemaHandler="${this.getMapGridSchema}"
                        grid-options='${JSON.stringify(grid_options)}'
                    ></ui-form>
                `;
            case 3:
                this.pageType = "ui-form";
                program = `${program}.Duplicates`;
                const page3Title = `Import Tables Duplicates - ${get(this.data, "Params.table", null)}`;

                const key_fields = [];
                this.tableFields.forEach(ele => {
                    key_fields.push([ele.name, ele.label]);
                });

                return html`
                <ui-form
                    owner-id="${this.instanceId}"
                    mode="${this.mode}"
                    program="${program}"
                    form-title="${page3Title}"
                >
                    <ui-combobox
                        label="Select How Duplicated Records are Handled"
                        name="Params.dups.duphandler"
                        value="${get(this.data, 'Params.dups.duphandler', 'Skip')}"
                        required="Duplicate Handler is a Required Field"
                        choices='[["Skip","Skip"], ["Overwrite","Overwrite"]]'
                        autofocus
                    ></ui-combobox>
                    <ui-combobox
                        label="Select Key Fields for Duplicate Records"
                        name="Params.dups.dupkeys"
                        value="${get(this.data, 'Params.dups.dupkeys', '')}"
                        required="Duplicate Keys is a Required Field"
                        choices='${JSON.stringify(key_fields)}'
                        multiple
                    ></ui-combobox>
                    <ui-combobox
                        label="Select Grouping Conditions for Key Fields"
                        name="Params.dups.dupkeycond"
                        value="${get(this.data, 'Params.dups.dupkeycond', 0)}"
                        required="Key Conditions is a Required Field"
                        choices='[[0, "All"], [1, "Any"], [2, "None"], [3, "Not All"]]'
                    ></ui-combobox>
                </ui-form>
                `;
            case 4:
                this.pageType = "ui-submittaskform";
                return html`
                <ui-submittaskform
                    owner-id="${this.instanceId}"
                    runscript="${this.runscript}"
                    program-name="${program}"
                    ruleset-rowid="${this.rowId}"
                    ruleset-title="${get(this.data, 'Title', null)}"
                    ruleset-params='${JSON.stringify(get(this.data, "Params", null))}'
                >
                </ui-submittaskform>
                `;
        };
    }

    render() {
        const stepsTemplate = [];
        this.steps.forEach((step, index) => {
            // To refer to hyphenated properties such as font-family,
            // use the camelCase equivalent (fontFamily) or
            // place the hyphenated property name in quotes ('font-family').
            const classes = {
                "step-primary": index === this.activeStep ? true : false,
                "cursor-pointer": index <= this.watermark && index !== this.activeStep ? true : false,
            };
            stepsTemplate.push(html`
                <li class="step ${classMap(classes)}" @click="${() => this.onStep(index)}">${step}</li>
            `);
        });

        let nextText = this.nextText;
        if(this.activeStep === (this.steps.length-1))  nextText = this.submitText;
        else if(this.activeStep > 0) nextText = this.nextOrigText;

        let cardTitle = this.title;
        if(!isEmpty(this.data.Title)) {
            cardTitle += ` - ${this.data.Title}`;
        }

        return html`
            <div class="card w-full bg-base-100 shadow-xl group overflow-y-auto">
                <div class="card-body">
                    ${this.title ?
                        html`<h2 class="card-title">${cardTitle}</h2>`
                    : html``}
                    <ul class="steps steps-horizontal">
                        ${stepsTemplate}
                    </ul>
                    <div class="form-control">
                        ${this.renderStep()}
                    </div>
                    <div class="card-actions flex justify-end">
                        <button
                            @click="${this.onCancel}"
                            class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary">
                            ${this.cancelText}
                        </button>
                        <button
                            ?disabled="${this.activeStep === 0}"
                            @click="${this.onBack}"
                            class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary">
                            ${this.backText}
                        </button>
                        <button data-next
                            ?disabled="${this.disableNextButton}"
                            @click="${this.onNext}"
                            class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary group-invalid:pointer-events-none group-invalid:opacity-30">
                            ${nextText}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
}
customElements.define("ui-import-tables", ImportTables)
