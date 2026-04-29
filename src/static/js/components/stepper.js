import { LitElement, html, css, nothing } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../css/tw.js'

import { set, get, isEmpty, isArray, isFunction, isNil, isNull } from "../utils"
import api from "../api"
import store from "../store"
import breadcrumbs from "../breadcrumb"
import { ConvertToJsonValues, FormTitle } from "./form/formutils"


class Stepper extends LitElement {
    static styles = [
        css `
            :host{
                height: 100%;
                overflow-y: auto;
            }
        `,
        TWStyles
    ];

    static instanceCounter = 0;

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },
        title: { attribute: "stepper-title", type: String },
        mode: { type: String },  // Create,Update,Delete
        dbTable: { attribute: "db-table", type: String },
        url: { type: String },
        rowId: { attribute: "row-id", type: Number },
        data: { type: Object },
        keyTitle: { attribute: "key-title", type: String},
        stepperTitleFields: { attribute: "stepper-title-fields", type: Array},

        cancelHandler: { attribute: "cancel-handler", type: String },
        backHandler: { attribute: "back-handler", type: String },
        nextHandler: { attribute: "next-handler", type: String },
        submitHandler: { attribute: "submit-handler", type: String },
        formSchemaHandler: { attribute: "form-schema-handler", type: String },

        cancelText: { attribute: "cancel-text", type: String },
        backText: { attribute: "back-text", type: String },
        nextText: { attribute: "next-text", type: String },
        submitText: { attribute: "submit-text", type: String },

        submitPostCreateHandler: { attribute: "submit-post-create-handler", type: String },
        submitPostUpdateHandler: { attribute: "submit-post-update-handler", type: String },
        submitPostDeleteHandler: { attribute: "submit-post-delete-handler", type: String },

        activeStep: { state: true },
        steps: { state: true },
        pages: { state: true },
        watermark: { state: true },
        disableNextButton: { state: true },
        schemaFields: { state: true },
        schemaPanels: { state: true },
        backButton: { state: true },
        nextButton: { state: true }
    };

    constructor() {
        super();
        this.instanceId = "Stepper-" + (++Stepper.instanceCounter).toString();

        // bind the event listener to reference the component instance
        this.handleNextButton = this.handleNextButton.bind(this);
        this.handleBackButton = this.handleBackButton.bind(this);
        this.handleNextButtonDisable = this.handleNextButtonDisable.bind(this);
        this.handleStepperMode = this.handleStepperMode.bind(this);
        this.handleUpdateData = this.handleUpdateData.bind(this);
        this.onCancel = this.onCancel.bind(this);
        this.onBack = this.onBack.bind(this);
        this.onNext = this.onNext.bind(this);
        this.onStep = this.onStep.bind(this);
        this.handleSlotChange = this.handleSlotChange.bind(this);
        this.handleFieldRegister = this.handleFieldRegister.bind(this);
        this.handleRequestData = this.handleRequestData.bind(this);
        this.handleRequestValue = this.handleRequestValue.bind(this);

        // defaults
        this.ownerId = null;
        this.owner = null;
        this.title = "";
        this.data = {};
        this.fieldTypes = {};
        this.dbTable = null;
        this.mode = null;
        this.url = null;
        this.rowId = null;
        this.keyTitle = null;
        this.stepperTitleFields = null;

        this.cancelText = "Cancel";
        this.backText = "Back";
        this.nextText = "Next";
        this.nextOrigText = "Next";
        this.submitText = "Submit";

        this.submitPostCreateHandler = null;
        this.submitPostUpdateHandler = null;
        this.submitPostDeleteHandler = null;

        this.formSchemaHandler = null;
        this.schemaFields = null;
        this.schemaPanels = null;

        this.steps = [];
        this.pages = [];
        this.activeStep = 0;
        this.watermark = 0;
        this.disableNextButton = false;

        this.backButton = true;
        this.nextButton = true;

        this.addEventListener(`next-button-${this.instanceId}`, this.handleNextButton);
        this.addEventListener(`back-button-${this.instanceId}`, this.handleBackButton);
        this.addEventListener(`submit-button-disable-${this.instanceId}`, this.handleNextButtonDisable);
        this.addEventListener(`stepper-mode-${this.instanceId}`, this.handleStepperMode);
        this.addEventListener(`stepper-update-data-${this.instanceId}`, this.handleUpdateData);
        this.addEventListener(`form-field-register-${this.instanceId}`, this.handleFieldRegister);
        this.addEventListener(`request-data-${this.instanceId}`, this.handleRequestData);
        this.addEventListener(`request-for-value`, this.handleRequestValue);
    }

    async connectedCallback() {
        super.connectedCallback();

        this.nextOrigText = this.nextText;

        if(this.dbTable) {
            await api.GET("/formSchema/" + this.dbTable, null).then(data => {
                this.schemaPanels = data.form_panels;
                this.schemaFields = data.form_fields;

                if(isNull(this.keyTitle)) {
                    this.keyTitle = this.schemaPanels[0].keyField;
                }
            });
        }
    }

    handleSlotChange() {
        const slotNodes = this.shadowRoot.querySelector('slot').assignedNodes({ flatten: true });
        let index = -1;
        let withActivePage = false;
        slotNodes.forEach((node) => {
            if(node instanceof HTMLElement &&
                isFunction(node.constructor) &&
                node.constructor.prototype instanceof LitElement &&
                node.localName === "ui-step") {
                index += 1;
                this.steps.push(node.title ? node.title : "");

                if(!isEmpty(this.data)) {
                    node.data = isEmpty(node.dataPanel) ? this.data : get(this.data, node.dataPanel);
                }
                node.ownerId = this.instanceId;
                node.owner = this;
                node.stepIndex = index;
                if(node.activePage) {
                    withActivePage = true;
                    this.activeStep = index;
                    this.watermark = index;
                    node.showPage(true, this.data);
                } else {
                    node.showPage(false);
                }
                this.pages.push(node);
            }
        })
        if(!withActivePage) {
            this.activeStep = 0;
            this.pages[0].showPage(true, this.data);
        }
        this.update(); // force re-render
    }

    handleBackButton(event) {
        this.backButton = event.detail.value;
    }

    handleNextButton(event) {
        this.nextButton = event.detail.value;
    }

    handleNextButtonDisable(event) {
        // events from Children Lit Components
        this.disableNextButton = event.detail.value;
        if(!isNil(event.detail.buttonText)) {
            this.nextText = event.detail.buttonText;
        } else this.nextText = this.nextOrigText;
    }

    handleStepperMode(event) {
        // events from Children Lit Components
        this.mode = event.detail.mode;
    }

    handleUpdateData(event) {
        if(!isEmpty(event.detail.panel)) {
            // panel
            set(this.data, event.detail.panel, event.detail.value ? event.detail.value : {});
        } else if(!isEmpty(event.detail.key)) {
            // form field
            set(this.data, event.detail.key, event.detail.value);
        } else {
            // grid row
            if(!isEmpty(event.detail.value)) {
                Object.keys(event.detail.value).forEach(key => {
                    set(this.data, key, event.detail.value[key]);
                });
            }
            this.rowId = !isNil(this.data.Id) ? this.data.Id : 0;
        }
        this.requestUpdate();
    }

    handleFieldRegister(event) {
        this.fieldTypes[event.detail.key] = event.detail.type;
    }

    handleRequestData(event) {
        event.detail.callback(this.data); // pass this.data to child
    }

    handleRequestValue(event) {
        const value = get(this.data, event.detail.key, null);
        if(value) {
            event.detail.reply(value);
            event.stopPropagation();
        }
    }

    onCancel(event) {
        if(this.cancelHandler) {
            const myFunction = window[this.cancelHandler];
            if (isFunction(myFunction)) {
                return myFunction(event, this.data);
            }
        }

        event.preventDefault();
        breadcrumbs.closePage();
    }

    onBack(event) {
        if(!this.pages[this.activeStep].handleBack(event, this.data, this.activeStep, this.steps.length-1)) return false;

        if(this.backHandler) {
            const myFunction = window[this.backHandler];
            if (isFunction(myFunction)) {
                return myFunction(event, this.data);
            }
        }

        event.preventDefault();
        this.pages[this.activeStep].showPage(false);
        this.activeStep -= 1;
        this.pages[this.activeStep].showPage(true, this.data);
    }

    async onNext(event) {
        if(!this.pages[this.activeStep].handleNext(event, this.data, this.activeStep, this.steps.length-1)) return false;

        if(this.activeStep === (this.steps.length-1))  {
            if(this.submitHandler) {
                const myFunction = window[this.submitHandler];
                if (isFunction(myFunction)) {
                    return myFunction(event, this.data);
                }
            }
        } else {
            if(this.nextHandler) {
                this.pages[this.activeStep].showPage(false);
                const myFunction = window[this.nextHandler];
                if (isFunction(myFunction)) {
                    return myFunction(event, this.data);
                }
            }
        }

        event.preventDefault();
        if(this.activeStep === (this.steps.length-1))  {
            // Step has handleSubmit
            if(this.pages[this.activeStep].node &&
                isFunction(this.pages[this.activeStep].node.handleSubmit)) {
                try {
                    this.pages[this.activeStep].node.handleSubmit();
                    breadcrumbs.closePage();
                } catch (err) {
                    console.log("stepper.onNext1 error:", err);
                    const message = `stepper.onNext1 ${err.status}  ${err.detail} : ${this.mode} ${(this.title) ? this.title : this.action}`;
                    const toaster = document.querySelector("[data-toaster]");
                    toaster.show(message,"error");
                }
                return;
            }

            // convert form data to json data payload
            if(!isEmpty(this.fieldTypes)) {
                ConvertToJsonValues(this.fieldTypes, this.data,
                    store.get("user.Settings.Locale")[0],
                    store.get("user.Settings.Timezone")[0]
                );
            }

            const stepperData = {
                "Depth": 1,
                "DbTableName": this.dbTable,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "RowId": this.rowId || 0,
                "Schema": { "form_panels": this.schemaPanels,
                            "form_fields": this.schemaFields
                            },
                "Data": this.data
            };
            try {
                let url = null;
                switch(this.mode) {
                    case "Create":
                        url = "/createTable";
                        if(!isEmpty(this.url)) url = this.url;
                        await api.POST(url, stepperData, "json")
                            .then(data => {
                                if(this.submitPostCreateHandler) {
                                    const myFunction = window[this.submitPostCreateHandler];
                                    if (isFunction(myFunction)) {
                                        return myFunction(event, data);
                                    }
                                }
                            });
                        break;
                    case "Update":
                        url = "/updateTable";
                        if(!isEmpty(this.url)) url = this.url;
                        await api.PUT(url, stepperData, "json")
                            .then(data => {
                                if(this.submitPostUpdateHandler) {
                                    const myFunction = window[this.submitPostUpdateHandler];
                                    if (isFunction(myFunction)) {
                                        return myFunction(event, data);
                                    }
                                }
                            });
                        break;
                    case "Delete":
                        url = "/deleteTable";
                        if(!isEmpty(this.url)) url = this.url;
                        await api.DELETE(url, stepperData, "json")
                            .then(data => {
                                if(this.submitPostDeleteHandler) {
                                    const myFunction = window[this.submitPostDeleteHandler];
                                    if (isFunction(myFunction)) {
                                        return myFunction(event, data);
                                    }
                                }
                            });
                }
                breadcrumbs.closePage();
            } catch (err) {
                console.log("stepper.onNext2 error:", err);
                const message = `stepper.onNext2 ${err.status}  ${err.detail} : ${this.mode} ${(this.title) ? this.title : this.action}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        } else {
            this.pages[this.activeStep].showPage(false);
            this.activeStep += 1;
            this.watermark = Math.max(this.watermark, this.activeStep);
            this.pages[this.activeStep].showPage(true, this.data);
        }
    }

    onStep(step) {
        if(step <= this.watermark) {
            if(step > this.activeStep && this.disableNextButton) {
                return false;
            }

            if(!this.pages[this.activeStep].handleStep(this.data, step, this.activeStep, this.steps.length-1)) return false;

            this.pages[this.activeStep].showPage(false);
            this.activeStep = step;
            this.pages[this.activeStep].showPage(true, this.data);
        }
    }

    getData() {
        if(this.owner)  return this.owner.getData();

        return this.data;
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

        const cardTitle = FormTitle(this.title, this.stepperTitleFields, this.data, this.keyTitle);

        return html`
            <div class="card w-full bg-base-100 shadow-xl group overflow-y-auto">
                <div class="card-body">
                    ${this.title ?
                        html`<h2 class="card-title">${cardTitle}</h2>`
                    : nothing }
                    <ul class="steps steps-horizontal">
                        ${stepsTemplate}
                    </ul>
                    <div class="form-control">
                        <slot @slotchange="${this.handleSlotChange}"></slot>
                    </div>
                    <div class="card-actions flex justify-end">
                        <button
                            @click="${this.onCancel}"
                            class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary">
                            ${this.cancelText}
                        </button>
                        ${this.backButton ?
                            html`<button
                                ?disabled="${this.activeStep === 0}"
                                @click="${this.onBack}"
                                class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary">
                                ${this.backText}
                            </button>`
                        : nothing }
                        ${this.nextButton ?
                            html`<button data-next
                                ?disabled="${this.disableNextButton}"
                                @click="${this.onNext}"
                                class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary group-invalid:pointer-events-none group-invalid:opacity-30">
                                ${nextText}
                            </button>`
                        : nothing }
                    </div>
                </div>
            </div>
        `;
    }
}
customElements.define("ui-stepper", Stepper)

class Step extends LitElement {

    static instanceCounter = 0;

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },
        title: { attribute: "step-title", type: String },
        dataPanel: { attribute: "data-panel", type: String },
        data: { type: Object },
        activePage: { attribute: "active-page", type: Boolean}, // this is the active page
        fetchData: { attribute: "fetch-data", type: Boolean},  // component will fetch data

        noNextButton: { attribute: "no-next-button", type: Boolean},
        noBackButton: { attribute: "no-back-button", type: Boolean},

        show: { state: true },

        nextText: { state: true },
        disableNextButton: { state: true }
    };

    constructor() {
        super();
        this.instanceId = "Step-" + (++Step.instanceCounter).toString();

        // bind the event listener to reference the component instance
        this.handleNextButtonDisable = this.handleNextButtonDisable.bind(this);
        this.handleStepMode = this.handleStepMode.bind(this);
        this.handleUpdateData = this.handleUpdateData.bind(this);
        this.handleBack = this.handleBack.bind(this);
        this.handleNext = this.handleNext.bind(this);
        this.handleStep = this.handleStep.bind(this);
        this.handleSlotChange = this.handleSlotChange.bind(this);
        this.handleFieldRegister = this.handleFieldRegister.bind(this);
        this.handleRequestData = this.handleRequestData.bind(this);

        this.ownerId = null;
        this.owner = null;
        this.stepIndex = null;
        this.activePage = false;
        this.fetchData = false;
        this.dataPanel = "";
        this.data = null;
        this.show = true;

        this.node = null;
        this.backNode = null;
        this.nextNode = null;
        this.stepNode = null;
        this.focusNode = null;

        this.nextText = "Next";
        this.nextOrigText = "Next";
        this.disableNextButton = false;

        this.noNextButton = false;
        this.noBackButton = false;

        this.addEventListener(`submit-button-disable-${this.instanceId}`, this.handleNextButtonDisable);
        this.addEventListener(`step-mode-${this.instanceId}`, this.handleStepMode);
        this.addEventListener(`grid-select-row-${this.instanceId}`, this.handleUpdateData);
        this.addEventListener(`form-field-updated-${this.instanceId}`, this.handleUpdateData);
        this.addEventListener(`form-field-register-${this.instanceId}`, this.handleFieldRegister);
        this.addEventListener(`request-data-${this.instanceId}`, this.handleRequestData);
    }

    handleSlotChange() {
        const slotNodes = this.shadowRoot.querySelector('slot').assignedNodes({ flatten: true });
        this.iterateNodes(slotNodes);
    }

    iterateNodes(nodes) {
        nodes.forEach((node) => {
            if(node instanceof HTMLElement) {
                if(isFunction(node.constructor) &&
                    node.constructor.prototype instanceof LitElement) {

                    node.ownerId = this.instanceId;
                    node.owner = this;

                    this.node = node;
                    if(this.data) {
                        node.setData(this.data);
                    }

                    if(node.handleStepperBack && isFunction(node.handleStepperBack))
                        this.backNode = node;
                    if(node.handleStepperNext && isFunction(node.handleStepperNext))
                        this.nextNode = node;
                    if(node.handleStepperStep && isFunction(node.handleStepperStep))
                        this.stepNode = node;
                    if(node.handleStepperFocus && isFunction(node.handleStepperFocus))
                        this.focusNode = node;

                    this.dispatchEvent(new CustomEvent(`form-field-register-${this.ownerId}`, {
                        bubbles: true,
                        composed: true,
                        detail: {
                            key: node.name,
                            type: node.fieldType
                        }
                    }));

                } else if (node.childNodes && node.childNodes.length > 0) {
                    // Recursively check children
                    this.iterateNodes(node.childNodes);
                }
            }
        });
    }

    handleBack(event, stepperData, activeStep, totalSteps) {
        if(this.backNode) {
            return this.backNode.handleStepperBack(event, this.dataPanel, stepperData, activeStep, totalSteps);
        }
        return true;
    }

    handleNext(event, stepperData, activeStep, totalSteps) {
        if(this.nextNode) {
            return this.nextNode.handleStepperNext(event, this.dataPanel, stepperData, activeStep, totalSteps);
        }
        return true;
    }

    handleStep(stepperData, step, activeStep, totalSteps) {
        if(this.stepNode) {
            return this.stepNode.handleStepperStep(this.dataPanel, step, stepperData, activeStep, totalSteps);
        }
        return true;
    }

    handleNextButtonDisable(event) {
        event.preventDefault();

        if(!this.show) {
            event.stopPropagation();
            return false;
        }

        // events from Children Lit Components
        this.disableNextButton = event.detail.value;
        if(!isNil(event.detail.buttonText)) {
            this.nextText = event.detail.buttonText;
        } else this.nextText = this.nextOrigText;
        // to ui-stepper parent
        this.dispatchEvent(new CustomEvent(`submit-button-disable-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                value: this.disableNextButton,
                buttonText: this.nextText
            }
        }));
    }

    handleStepMode(event) {
        event.preventDefault();
        // to ui-stepper parent
        this.dispatchEvent(new CustomEvent(`stepper-mode-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                mode: event.detail.mode
            }
        }));
    }

    handleUpdateData(event) {
        let sender = event.detail.sender ? event.detail.sender : [];
        sender.push(`${this.instanceId}.handleUpdateData`);
        // to ui-stepper parent from form or datatable step component
        this.dispatchEvent(new CustomEvent(`stepper-update-data-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                key: event.detail.key,
                value: event.detail.value,
                panel: this.dataPanel,
                sender: sender
            }
        }));
    }

    handleFieldRegister(event) {
        this.dispatchEvent(new CustomEvent(`form-field-register-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                key: event.detail.key,
                type: event.detail.type
            }
        }));
    }

    handleRequestData(event) {
        // request data from Stepper
        this.dispatchEvent(new CustomEvent(`request-data-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                callback: (data) => {
                    event.detail.callback(data); // pass this.data to child
                }
            }
        }));
    }

    showPage(value, stepperData=null) {
        this.show = value;
        if(this.show) {
            // to ui-stepper parent
            this.dispatchEvent(new CustomEvent(`back-button-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    value: !this.noBackButton
                }
            }));
            this.dispatchEvent(new CustomEvent(`next-button-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    value: !this.noNextButton
                }
            }));
            if(!isNull(this.node)) {
                if(!isNull(stepperData)) {
                    if(!this.fetchData) {
                        this.node.setData(!isEmpty(this.dataPanel) ? stepperData[this.dataPanel] : stepperData);
                    }
                    else {
                        this.node.reload();
                    }
                }
                if(this.focusNode) {
                    this.focusNode.handleStepperFocus();
                }
                // to ui-stepper parent
                this.dispatchEvent(new CustomEvent(`submit-button-disable-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: {
                        value: this.disableNextButton,
                        buttonText: this.nextText
                    }
                }));
            }
        }
    }

    getData() {
        if(this.owner)  return this.owner.getData();

        return this.data;
    }

    render() {
        return html`
            <style>
                :host {
                    display: ${this.show ? 'block' : 'none'};
                }
            </style>
            <slot @slotchange="${this.handleSlotChange}"></slot>
        `;
    }
}

customElements.define("ui-step", Step)
