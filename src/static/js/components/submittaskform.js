import { LitElement, html, css } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../css/tw.js'

import api from "../api"
import store from "../store"
import breadcrumbs from "../breadcrumb"
import { isNil, set, isNull, isEmpty } from "../utils"

class SubmitTaskForm extends LitElement {
    static styles = [css ``, TWStyles];

    static instanceCounter = 0;

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },
        runScript: { attribute: "runscript", type: String },
        program: { attribute: "program-name", type: String },
        programType: { attribute: "program-type", type: String },

        rulesetRowId: { attribute: "ruleset-rowid", type: Number },
        rulesetTitle: { attribute: "ruleset-title", type: String },
        rulesetParams: { attribute: "ruleset-params", type: String },

        documentValidValues: { attribute: "document-values", type: Object },
        deviceValidValues: { attribute: "device-values", type: Object },
        notifyValidValues: { attribute: "notify-values", type: Object },

        okToRender: { state: true },
    };

    constructor() {
        super();
        this.instanceId = "SubmitTaskForm-" + (++SubmitTaskForm.instanceCounter).toString();

        this.getTaskSchema = this.getTaskSchema.bind(this);
        this.handleUpdateData = this.handleUpdateData.bind(this);
        this.handleStepperNext = this.handleStepperNext.bind(this);
        this.handleNextButtonDisable = this.handleNextButtonDisable.bind(this);

        this.program = null;
        this.programType = "Script";
        this.programId = null;
        this.runScript = null;

        this.rulesetTitle = "";
        this.rulesetParams = null;
        this.rulesetRowId = 0;

        this.rulesetSchema = null;
        this.taskSchema = null;

        this.documentValidValues = ["pdf"];
        this.deviceValidValues = ["spooler"];
        this.notifyValidValues = ["Never","Always"];

        this.data = {};

        this.okToRender = false;

        this.addEventListener(`form-field-updated-${this.instanceId}`, this.handleUpdateData);
        this.addEventListener(`submit-button-disable-${this.instanceId}`, this.handleNextButtonDisable);
    }

    connectedCallback() {
        super.connectedCallback();

        if(!isEmpty(this.rulesetTitle)) {
            // not created by ui-step
            this.setupSchema();
        }
    }

    async setupSchema() {
        await api.GET(`/getProgram/${this.program}/${this.programType}/1`, null)
            .then(data => {
                this.programId = data.data.Id;
        });

        await api.GET("/formSchema/Rulesets", null).then(data => {
            this.rulesetSchema = {
                "form_panels": data.form_panels,
                "form_fields": data.form_fields
            };
        });

        const skipColumns = ["Company","Role","Program","User","RunScript", "Title", "Params", "Status", "Session"];
        if(this.documentValidValues.length === 1) {
            skipColumns.push("Document");
            const params = {
                "Depth": 1,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "FieldList": [],
                "Mode": "Update",
                "ChoicesAsTuple": true,
                "ChoicesKey": false,
                "TextAsString": true,
                "DbTableName": "Documents",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "Document", "op": 0, "value": this.documentValidValues[0]}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                     set(this.data, "Document", data.data);
                });
        }
        if(this.deviceValidValues.length === 1) {
            skipColumns.push("Device");
            const params = {
                "Depth": 1,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "FieldList": [],
                "Mode": "Update",
                "ChoicesAsTuple": true,
                "ChoicesKey": false,
                "TextAsString": true,
                "DbTableName": "Devices",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "Device", "op": 0, "value": this.deviceValidValues[0]}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                     set(this.data, "Device", data.data);
                });
        }

        await api.GET("/formSchema/Tasks", null).then(data => {
            const schemaFields = [];
            data.form_fields.forEach(field => {
                if(skipColumns.includes(field.name)) {
                    field["modifiable"] = false;
                } else {
                    field["modifiable"] = true;
                    field.autoDefault = true;
                    if(field.name === "Document") {
                        field.validValuesKey = "Type";  // Documents.Type
                        field.validValues = this.documentValidValues;
                    } else if(field.name === "Device") {
                        field.validValuesKey = "Type";  // Devices.Type
                        field.validValues = this.deviceValidValues;
                    } else if(field.name === "Notify") {
                        field.validValues = this.notifyValidValues;
                    }
                }
                schemaFields.push(field);
            });
            this.taskSchema = {
                "form_panels": data.form_panels,
                "form_fields": schemaFields
            };

            this.okToRender = true;
        });
    }

    async getTaskSchema() {
        return this.taskSchema;
    }

    handleUpdateData(event) {
        set(this.data, event.detail.key, event.detail.value);
    }

    handleNextButtonDisable(event) {
        // bubble up event to owner
        this.dispatchEvent(new CustomEvent(`submit-button-disable-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: event.detail
        }));
    }

    // called by owner
    handleStepperNext(event, panel, stepperData, activeStep, totalSteps) {
        // Validate all fields before submitting the form
        const page = this.shadowRoot.querySelector("ui-form");
        if(page)
            return page.handleStepperNext(event, "", this.data, activeStep, totalSteps);
        return true;
    }

    // called by owner
    async handleSubmit() {
        const ruleset_data = {
            "Depth": 1,
            "DbTableName": "Rulesets",
            "CompanyRowId": store.get("user.Company_Id"),
            "Locale": store.get("user.Settings.Locale")[0],
            "Timezone": store.get("user.Settings.Timezone")[0],
            "RowId": this.rulesetRowId,
            "Schema": this.rulesetSchema,
            "Data": {
                "Company": store.get("user.Company_Id"),
                "Program": this.programId,
                "Role": store.get("user.Role_Id"),
                "User": store.get("user.Id"),
                "Title": this.rulesetTitle,
                "Params": this.rulesetParams
            }
        }

        const task_record = this.data;
        task_record.Company = store.get("user.Company_Id");
        task_record.Role = store.get("user.Role_Id");
        task_record.Program = this.programId;
        task_record.User = store.get("user.Id");
        task_record.RunScript = this.runScript;
        task_record.Title = this.rulesetTitle;
        task_record.Params = this.rulesetParams;
        task_record.Session = {
            "locale": store.get("user.Settings.Locale")[0],
            "timezone": store.get("user.Settings.Timezone")[0]
        };

        const task_data = {
            "Depth": 1,
            "DbTableName": "Tasks",
            "CompanyRowId": store.get("user.Company_Id"),
            "Locale": store.get("user.Settings.Locale")[0],
            "Timezone": store.get("user.Settings.Timezone")[0],
            "RowId": 0,
            "Schema": this.taskSchema,
            "Data": task_record
        }

        try {
            if(this.rulesetRowId > 0) {
                await api.PUT("/updateTable", ruleset_data, "json")
                    .then(() => {
                        api.POST("/createTable", task_data, "json");
                    });
            } else {
                await api.POST("/createTable", ruleset_data, "json")
                    .then(() => {
                        api.POST("/createTable", task_data, "json");
                    });
            }
            breadcrumbs.closePage();
        } catch (err) {
            console.log("submittaskform.handleSubmit error:", err);
            const message = `submittaskform.handleSubmit ${err.status}  ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    reload() {
        // called by ui-step  for fetch-data ui-step
        if(!this.okToRender) this.setupSchema();
        else this.requestUpdate();
    }

    // called by ui-step not fetch-data ui-step (fetch-data see reload())
    setData(data) {
        if(!this.okToRender) this.setupSchema();

        this.rulesetTitle = isEmpty(data.Title) ? this.rulesetTitle : data.Title;
        this.rulesetParams = data.Params;
        this.rulesetRowId = isEmpty(data.Id) ? 0 : data.Id;
    }

    shouldUpdate(changedProperties) {
        // check if can render
        return this.okToRender;
    }

    render() {
        let title = "Submit Task";
        if(!isEmpty(this.rulesetTitle))  title += ` - ${this.rulesetTitle}`;

        return html`
            <ui-form
                owner-id="${this.instanceId}"
                owner="${this}"
                form-title="${title}"
                program="SubmitTaskForm"
                db-table="Tasks"

                .getFormSchemaHandler="${this.getTaskSchema}"
            >
            </ui-form>
        `;
    }
}

customElements.define("ui-submittaskform", SubmitTaskForm)
