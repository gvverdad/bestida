import { LitElement, html, css } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../../../css/tw.js'
import * as XLSX from 'xlsx';

import store from "../../../../js/store"
import breadcrumbs from "../../../../js/breadcrumb"
import { isNil, isEmpty, isArray, get, set } from "../../../../js/utils"

class Audit extends LitElement {
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
        this.instanceId = "Audit-" + (++Audit.instanceCounter).toString();

        this.handleNextButtonDisable = this.handleNextButtonDisable.bind(this);
        this.handleUpdateData = this.handleUpdateData.bind(this);
        this.getGridSchema = this.getGridSchema.bind(this);
        this.getGridData = this.getGridData.bind(this);

        this.onCancel = this.onCancel.bind(this);
        this.onBack = this.onBack.bind(this);
        this.onNext = this.onNext.bind(this);
        this.onStep = this.onStep.bind(this);

        this.title = null;

        this.steps = ["Table", "History"];
        this.activeStep = 0;
        this.watermark = 0;
        this.program = null;

        this.rowId = null;
        this.mode = "Create"; // Create,Update,Delete

        this.disableNextButton = true;

        this.cancelText = "Cancel";
        this.backText = "Back";
        this.nextText = "Next";

        this.table = null;

        this.addEventListener(`submit-button-disable-${this.instanceId}`, this.handleNextButtonDisable);
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

        if(!isEmpty(this.table)) this.disableNextButton = false;
    }

    onNext(event) {
        event.preventDefault();

        this.activeStep += 1;
        this.watermark = Math.max(this.watermark, this.activeStep);
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
    }

    handleUpdateData(event) {
        this.table = event.detail.value;
    }

    async getGridSchema() {
        try {
            return api.GET(`/auditGridSchema/${this.table}`, null)
                .then(data => {
                    let grid_fields = [];
                    data.grid_fields.forEach( field => {
                        const options = {
                            "sort": false,
                            "sortDirection": "none",
                            "display": field.visible,
                            "modifiable": false
                        };
                        if (field.name.startsWith("CreateOpId")) {
                            options.display = false;
                        } else if (field.name === "CreateTimeStamp") {
                            options.display = false;
                        } else if (field.name.startsWith("ModifiedOpId")) {
                            options.display = false;
                        } else if (field.name === "ModifiedTimeStamp") {
                            options.display = false;
                        }
                        field["options"] = options;
                        grid_fields.push(field);
                    });
console.log("audit.getGridSchema:", data.grid_tables, grid_fields);
                    return {"grid_fields": grid_fields,
                            "grid_tables": data.grid_tables};
                });
        } catch (err) {
            console.log("audit.getGridSchema error", this.table, err);
            const message = `${err.status}  ${err.detail} : audit.getGridSchema ${this.dbTable}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    getGridData(grid_columns, criteria, criteria_type, page, pagesize) {
        try {
            const params = {
                "Depth": 1,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "FieldList": [],
                "DbTableName": this.table,
                "Criteria": criteria,
                "CriteriaType": criteria_type, // ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3
                "Columns": grid_columns,
                "Offset": page * (pagesize > 0 ? pagesize : 0),
                "PageSize": pagesize,
                "ChoicesAsTuple": false,
                "ChoicesKey": true,
                "TextAsString": true,
                "Draw": 1
            };
            return api.POST("/auditList", params, "json");
        } catch(err) {
            console.log("audit.getGridData error", this.table, err);
            const message = `${err.status}  ${err.detail} : audit.getGridData ${this.table}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    renderStep() {
        let program = this.program;
        switch(this.activeStep) {
            case 0:
                program = `${program}.Table`;
                return html`
                    <ui-form
                        owner-id="${this.instanceId}"
                        mode="${this.mode}"
                        program="${program}"
                        form-title="Table"
                    >
                        <ui-combobox label="Table"
                            name="table"
                            value="${this.table}"
                            required="Table is a Required Field"
                            enum-getter="getVersionedTablesList"
                        ></ui-combobox>
                   </ui-form>
                `;
            case 1:
                program = `${program}.History.${this.table}`;
                return html`
                    <ui-datatable
                        owner-id="${this.instanceId}"
                        grid-title="${`History - ${this.table}`}"
                        db-table="${this.table}"
                        program="${program}"
                        filter-button
                        column-button
                        refresh-button
                        download-button
                        print-button

                        .getGridDataHandler="${this.getGridData}"
                        .getGridSchemaHandler="${this.getGridSchema}"

                    ></ui-datatable>
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

        if(this.activeStep === (this.steps.length-1)) this.disableNextButton = true;

        return html`
            <div class="card w-full bg-base-100 shadow-xl group overflow-y-auto">
                <div class="card-body">
                    ${this.title ?
                        html`<h2 class="card-title">${this.title}</h2>`
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
                            ${this.nextText}
                        </button>
                    </div>
                </div>
            </div>
        `;
    }
}
customElements.define("ui-audit", Audit)
