import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../css/tw.js'
import { classMap } from 'lit/directives/class-map.js';

import breadcrumbs from "../../breadcrumb";
import "./panel"
import api from "../../api"
import store from "../../store"
import { CreateValidationSchema, ExtractNodeValidators, ConvertToJsonValues,
        ConvertToFormValues, CreateValidationContext, FormTitle,
        CreateFormValidator, ValidateFields, ActionOn, Cascade } from "./formutils"
import { isFunction, isNull, isEmpty, isNil, isArray, get, set } from "../../utils"

class Form extends LitElement {
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
        // form is a component of owner (Stepper or Datatable)
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },
        title: { attribute: "form-title", type: String },
        // api Create,Copy,Update,Delete
        mode: { type: String }, // Create, Copy, Update, Delete
        // REST - use either api mode or REST action/method
        // action is url
        action: { attribute: "action", type: String },
        // method post (Create), put (Update), delete (Delete)
        method: { attribute: "method", type: String },

        // will build form based on dbTable properties
        dbTable: { attribute: "db-table", type: String },
        // program name to save program state in child components ie. datatables
        program: { type: String },
        // security to pass to child components ie. datatables
        securityLevel: { attribute: "security-level", type: Object },

        // display mode in title as prefix
        modeInTitle: { attribute: "mode-in-title", type: Boolean },

        formFields: { attribute: "form-fields", type: Array},
        keyTitle: { attribute: "key-title", type: String},
        excludeFields: { attribute: "exclude-fields", type: Array},
        rowId: { attribute: "row-id", type: Number },
        formType: { attribute: "form-type", type: String },

        formData: { attribute: "initial-values", type: Object },
        validationSchema: { attribute: "validation-schema", type: String },

        grid: { type: String },  // grid component
        // form components that listens to grid component event
        gridListeners: { attribute: "grid-listeners", type: Object },

        // ui-combobox to default first option item
        autoDefault: { attribute: "auto-default", type: Boolean },

        localData: { attribute: "local-data", type: Boolean },
        // use form buttons - Stepper has buttons too
        formButtons: { attribute: "form-buttons", type: Boolean },
        // use form cancel button
        formButtonCancel: { attribute: "form-button-cancel", type: Boolean },
        // use form submit button
        formButtonSubmit: { attribute: "form-button-submit", type: Boolean },
        cancelHandler: { attribute: "cancel-handler", type: String },
        submitHandler: { attribute: "submit-handler", type: String },
        nextHandler: { attribute: "next-handler", type: String },
        backHandler: { attribute: "back-handler", type: String },
        stepHandler: { attribute: "step-handler", type: String },

        refreshAfterSubmit: { attribute: "refresh-after-submit", type: Boolean },
        submitPostPutHandler: { attribute: "submit-post-put-handler", type: String },
        submitPostDeleteHandler: { attribute: "submit-post-delete-handler", type: String },
        submitPostPostHandler: { attribute: "submit-post-post-handler", type: String },

        ownerCancelHandler: { attribute: "owner-cancel-handler", type: Boolean },
        ownerSubmitHandler: { attribute: "owner-submit-handler", type: Boolean },
        ownerSubmitPostPutHandler: { attribute: "owner-submit-post-put-handler", type: Boolean },
        ownerSubmitPostDeleteHandler: { attribute: "owner-submit-post-delete-handler", type: Boolean },
        ownerSubmitPostPostHandler: { attribute: "owner-submit-post-post-handler", type: Boolean },

        getFormSchemaHandler: { type: Function },
        getFormDataHandler: { type: Function },
        getFormDataURL: { attribute: "get-data-url", type: String },
        getFormSchemaURL: { attribute: "get-schema-url", type: String },

        formValidator: { type: Function },

        getGridSchemaHandler: { type: Function },
        getGridDataHandler: { type: Function },
        gridOptions: { attribute: "grid-options", type: Object },

        // cancel button text, default to Cancel
        cancelText: { attribute: "cancel-text", type: String },
        // submit button text, default to Submit
        submitText: { attribute: "submit-text", type: String },

        parentTable: { attribute: "parent-table", type: String },
        parentField: { attribute: "parent-field", type: String },
        parentRowId: { attribute: "parent-row-id", type: Number },
        parentRow: { attribute: "parent-row", type: Object },
        joinList: { attribute: "join-list", type: Array },

        errors: { state: true },
        schemaFields: { state: true },
        schemaPanels: { state: true },
        okToRender: { state: true },
        activeStep: { state: true }
    };

    constructor() {
        super();
        this.instanceId = "Form-" + (++Form.instanceCounter).toString();

        // bind the event listener to reference the component instance
        this.handleFieldRegister = this.handleFieldRegister.bind(this);
        this.handleNodeRegister = this.handleNodeRegister.bind(this);
        this.handleFieldUpdate = this.handleFieldUpdate.bind(this);
        this.handleFieldBlur = this.handleFieldBlur.bind(this);
        this.handleElementUpdate = this.handleElementUpdate.bind(this);
        this.handleElementBlur = this.handleElementBlur.bind(this);
        this.onSlotChange = this.onSlotChange.bind(this);
        this.handleStepperBack = this.handleStepperBack.bind(this);
        this.handleStepperNext = this.handleStepperNext.bind(this);
        this.handleStepperStep = this.handleStepperStep.bind(this);
        this.handleStepperFocus = this.handleStepperFocus.bind(this);
        this.handleSubmitButtonDisable = this.handleSubmitButtonDisable.bind(this);
        this.onCancel = this.onCancel.bind(this);
        this.onSubmit = this.onSubmit.bind(this);
        this.handleGridEvents = this.handleGridEvents.bind(this);
        this.afterSubmitRefresh = this.afterSubmitRefresh.bind(this);
        this.handleRequestForValue = this.handleRequestForValue.bind(this);

        // local stepper
        this.onStep = this.onStep.bind(this);
        this.onNext = this.onNext.bind(this);
        this.onBack = this.onBack.bind(this);

        this.handleDeleteSubmit = this.handleDeleteSubmit.bind(this);

        // defaults
        this.ownerId = null;
        this.owner = null;
        this.title = "";
        this.program = null;
        this.modeInTitle = false;

        this.mode = null;
        this.dbTable = null;
        this.rowId = 0;
        this.formFields = [];
        this.excludeFields = [];
        this.formType = null;
        this.keyTitle = null;

        this.method = null;
        this.validationSchema = null;
        this.localData = false;

        this.formData = {};
        this.formDataTypes = {};
        this.fieldNodes = {};
        this.errors = {};
        this.errorMessageNodes = {};
        this.validationList = [];
        this.submitButton = null;

        this.autoDefault = false;  // ui-combobox to default to first option item

        this.formButtons = false;
        this.formButtonCancel = false;
        this.formButtonSubmit = false;
        this.cancelText = "Cancel";
        this.submitText = "Submit";

        this.getFormSchemaHandler = null;
        this.getFormDataHandler = null;
        this.getFormDataURL = null;
        this.getFormSchemaURL = null;

        this.formValidator = null;

        this.getGridSchemaHandler = null;
        this.getGridDataHandler = null;
        this.gridOptions = null;

        // named function handlers
        this.cancelHandler = null;
        this.submitHandler = null;
        this.submitPostPutHandler = null;
        this.submitPostDeleteHandler = null;
        this.submitPostPostHandler = null;
        this.backHandler = null;
        this.nextHandler = null;
        this.stepHandler = null;

        this.refreshAfterSubmit = false;

        // owner event handlers
        this.ownerCancelHandler = false;
        this.ownerSubmitHandler = false;
        this.ownerSubmitPostPutHandler = false;
        this.ownerSubmitPostPostHandler = false;
        this.ownerSubmitPostDeleteHandler = false;

        this.schemaFields = null;
        this.schemaPanels = null;
        this.stepperTitleFields = null;  // Array
        this.okToRender = false;

        this.parentTable = null;
        this.parentField = null;
        this.parentRowId = 0;
        this.parentRow = null;
        this.joinList = null;

        this.errorFocused = false;

        // form as stepper
        this.isWizard = false;
        this.activeStep = 0;
        this.watermark = 0;
        this.nextButton = null;
        this.disableNextButton = true;
        this.backText = "Back";
        this.nextText = "Next";
        this.nextOrigText = "Next";

        this.securityLevel = {
            "runLevel": 999,
            "createLevel": 999,
            "updateLevel": 999,
            "deleteLevel": 999
        };

        this.grid = null;
        this.gridListeners = null;

        this.addEventListener(`form-field-updated-${this.instanceId}`, this.handleFieldUpdate);
        this.addEventListener(`form-field-blur-${this.instanceId}`, this.handleFieldBlur);
        this.addEventListener(`form-field-register-${this.instanceId}`, this.handleFieldRegister);
        this.addEventListener(`form-node-register-${this.instanceId}`, this.handleNodeRegister);
        this.addEventListener(`form-delete-cancel-${this.instanceId}`, this.onCancel);
        this.addEventListener(`form-delete-submit-${this.instanceId}`, this.handleDeleteSubmit);

        this.addEventListener(`submit-button-disable-${this.instanceId}`, this.handleSubmitButtonDisable);
        this.addEventListener(`grid-events-${this.instanceId}`, this.handleGridEvents);

        this.addEventListener(`request-for-value`, this.handleRequestForValue);
    }

    async connectedCallback() {
        super.connectedCallback();

        if(this.modeInTitle && this.mode) {
            this.title = `${this.mode} ${this.title}`;
        }
        this.nextOrigText = this.nextText;
        this.disableNextButton = true;

        if(this.dbTable) {
            const emptyData = isEmpty(this.formData);
            this.disableNextButton = false;

            await this.getFormSchema();
            // this.getFormSchema() populates this.formData with default data
            // so cannot check if(isEmpty(this.formData))
            if(emptyData) {
                if(this.mode === "Create")
                    this.disableNextButton = true;
                // get data using this.rowid when this.formData is empty
                await this.getFormData();
            }

            if(isNull(this.keyTitle)) {
                this.keyTitle = this.schemaPanels[0].keyField;
            }

            // deep copy
            this.formData = structuredClone(ConvertToFormValues(this.formDataTypes,
                                    this.formData,
                                    store.get("user.Settings.Locale")[0],
                                    store.get("user.Settings.Timezone")[0]));

            this.okToRender = true;
        }
        else this.okToRender = true;
    }

    onSlotChange(event) {
        const slotNodes = this.shadowRoot.querySelector('slot').assignedNodes({ flatten: true });
        this.iterateNodes(slotNodes);

        if(this.validationSchema) {
            const myFunction = window[this.validationSchema];
            if (isFunction(myFunction)) {
                this.validationSchema = myFunction();
            } else {
                this.validationSchema = null;
            }
        }
        if(isNull(this.validationSchema)) {
            this.validationSchema = CreateValidationSchema(this.validationList);

            if(this.formValidator) {
                this.validationSchema = CreateFormValidator(this.formValidator,
                                                            this.fieldNodes,
                                                            this.validationSchema);
            }
        }
    }

    async iterateNodes(nodes) {
        nodes.forEach(async node => {
            if (node instanceof HTMLElement) {
                // Check if node is a form element
                if(node.getAttribute("type") === "submit" || node.getAttribute("data-submit_page")) {
                    this.submitPage = node;
                } else if(['input', 'textarea', 'select'].includes(node.tagName.toLowerCase())) {
                    this.populateValidationList(node, false);
                    this.populateFormData(node, true);
                } else if (isFunction(node.constructor) &&
                           node.constructor.prototype instanceof LitElement) {

                    node.ownerId = this.instanceId;
                    node.owner = this;
                    if(node.localName === "ui-combobox") {
                        node.formData = this.formData;
                        node.parentRow = this.parentRow;
                    }

                    let value = "";
                    if(!isNil(get(this.formData, node.name, null))) {
                        value = get(this.formData, node.name, "");
                        await node.setFieldValue(value);
                    } else if(!isNull(node.value)) {
                        value = node.value;
                        set(this.formData, node.name, value);
                    } else {
                        set(this.formData, node.name, value);
                    }

                    if(!isEmpty(this.grid) && !isEmpty(this.gridListeners) &&
                        node.name === this.grid) {
                        node.setListeners(this.gridListeners, this.formData);
                    }

                    if(node.type !== "hidden") this.populateValidationList(node, true);
                    this.addFieldNode(node, true);

                    // to ui-stepper
                    this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                        bubbles: true,
                        composed: true,
                        detail: {
                            key: node.name,
                            value: value,
                            type: node.type,
                            record: null,
                            sender: [`${this.instanceId}.iterateNodes`]
                        }
                    }));
                } else if(node.getAttribute("data-error")) {
                    const fieldName = node.getAttribute("data-error");
                    this.errorMessageNodes[fieldName] = node;
                }

                // Recursively check children
                if (node.childNodes && node.childNodes.length > 0) {
                    this.iterateNodes(node.childNodes);
                }
            }
        });
    }

    addFieldNode(node, lit=false) {
        this.fieldNodes[node.name] = {"node": node, "isLit": lit};
    }

    populateValidationList(node, lit=false) {
        const element = ExtractNodeValidators(node, lit);
        if(element) {
            if(this.validationSchema) {
                this.validationSchema = CreateValidationSchema([element], null, this.validationSchema);
            } else this.validationList.push(element);
        }
    }

    async getFormSchema() {
        const initialValues = isEmpty(this.formData);
        try {
            if (this.getFormSchemaHandler) {
                const data = await this.getFormSchemaHandler();
                this.schemaFields = [];
                this.stepperTitleFields = data.stepper_title_fields ? data.stepper_title_fields : null;
                data.form_panels.forEach(panel => {
                    const panel_fields = data.form_fields.filter(obj => obj.table === panel.table);
                    panel_fields.forEach(field => {
                        if(field["modifiable"]) {
                            this.schemaFields.push(field);
                            this.formDataTypes[field.name] = field.type;
                        }
                        if(initialValues) {
                            let value = "";
                            if(field.textType === "Dict") value = {};
                            else if(field.textType === "List") value = [];
                            else value = isEmpty(field.default) ? "" : field.default;
                            set(this.formData, field.name, value);
                        }
                    });
                });
                this.schemaPanels = data.form_panels;
                if(data.form_panels.length > 1) this.isWizard = true;
            } else {
                let path_query = `/formSchema/${this.dbTable}`;
                if(this.getFormSchemaURL) path_query = this.getFormSchemaURL;
                if(this.parentTable) {
                    path_query += "?level=1&main_form=false";
                }

                await api.GET(path_query, null).then(data => {
                    this.schemaFields = [];
                    this.stepperTitleFields = data.stepper_title_fields ? data.stepper_title_fields : null;
                    data.form_panels.forEach(panel => {
                        if(panel.use_list && initialValues) {
                            set(this.formData, panel.id, []);
                        }

                        const panel_fields = data.form_fields.filter(obj => obj.table === panel.table);
                        panel_fields.forEach(field => {
                            let isOK = true;
                            if(!isEmpty(this.excludeFields)) {
                                if(this.excludeFields.includes(field.name)) {
                                    isOK = false;
                                }
                            }
                            if(isOK) {
                                if(panel.use_list) {
                                    field["modifiable"] = false;
                                } else {
                                    if(!isEmpty(this.formFields)) {
                                        field["modifiable"] = false;
                                        if(this.formFields.includes(field.name)) {
                                            field.modifiable = true;
                                        }
                                    }
                                }
                                if(initialValues) {
                                    let value = "";
                                    if(field.textType === "Dict") value = {};
                                    else if(field.textType === "List") value = [];
                                    else value = isEmpty(field.default) ? "" : field.default;
                                    set(this.formData, field.name, value);
                                }

                                this.schemaFields.push(field);
                                this.formDataTypes[field.name] = field.type;
                            }
                        });
                    });
                    this.schemaPanels = data.form_panels;
                    if(data.form_panels.length > 1) this.isWizard = true;
                });
            }
        } catch (err) {
            console.log("form.getFormSchema error:", err);
            const message = `form.getFormSchema ${err.status}  ${err.detail} : form.getFormSchema ${this.dbTable}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    async getFormData() {
        try {
            if(this.rowId > 0) {
                if(this.getFormDataHandler) {
                    const data = await this.getFormDataHandler();
                    this.formData = data.data;
                } else {
                    const data = {
                        "Depth": 1,
                        "CompanyRowId": store.get("user.Company_Id"),
                        "Locale": store.get("user.Settings.Locale")[0],
                        "Timezone": store.get("user.Settings.Timezone")[0],
                        "FieldList": [],
                        "DbTableName": this.dbTable,
                        "RowId": this.rowId,
                        "Mode": this.mode === "Copy" ? "Update" : this.mode,
                        "TextAsString": true
                    };
                    let url = "/formData";
                    if(this.getFormDataURL) url = this.getFormDataURL;
                    await api.POST(url, data, "json")
                        .then(data => {
                            this.formData = data.data;
                            if(this.ownerId) {
                                this.dispatchEvent(new CustomEvent(`form-data-${this.ownerId}`, {
                                    bubbles: true,
                                    composed: true,
                                    detail: { value: data.data }
                                }));
                            }
                        });
                }
            }
        } catch (err) {
            console.log("form.getFormData error:", err);
            const message = `form.getFormData ${err.status}  ${err.detail} : form.getFormData ${this.dbTable}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    setData(data) {
        // setData from parent components ie: ui-stepper
        // deepcopy
        this.formData = ConvertToFormValues(this.formDataTypes, data,
                    store.get("user.Settings.Locale")[0], store.get("user.Settings.Timezone")[0]);

        this.localData = true;
        Object.keys(this.fieldNodes).forEach(async name => {
            const node = this.fieldNodes[name];
            if(node.isLit) {
                if(!isNull(get(this.formData, name, null))) {
                    await node.node.setFieldValue(get(this.formData, name, ""));
                } else if(!isNull(node.node.value)) {
                    set(this.formData, name, node.node.value);
                } else set(this.formData, name,  "");
            } else {
                this.populateFormData(node.node, false);
            }
            if(!isEmpty(this.grid) && !isEmpty(this.gridListeners) &&
                node.node.name === this.grid) {
                node.node.setListeners(this.gridListeners, this.formData);
            }
        });
    }

    // populate children NON Lit components form data
    populateFormData(element, init=true) {
        const { name, type, value, checked } = element;

        if(!name) return;

        if(init) {
            element.addEventListener('input', () => this.handleElementUpdate(element));
            element.addEventListener('blur', () => this.handleElementBlur(element));
            this.fieldNodes[name] = {"node": element, "isLit": false};
        }

        if (type === 'checkbox') {
            if(init) {
                if(get(this.formData, name) === true) {
                    element.checked = true;
                } else {
                    set(this.formData, name, false);
                    element.checked = false;
                }
            } else {
                set(this.formData, name, checked);
            }
        } else if (type === 'radio') {
            // TODO: Handle radio buttons
            if (checked) {
                if(!init) {
                    set(this.formData, name, value);
                }
            }
        } else if (type === 'select-one' || type === 'select-multiple') {
            // Handle select elements
            if(init) {
                element.value = get(this.formData, name, "");
            } else {
                const selectedOptions = Array.from(element.selectedOptions).map(option => option.value);
                set(this.formData, name, type === 'select-one' ? selectedOptions[0] : selectedOptions);
            }
        } else {
            if(init) {
                element.value = get(this.formData, name, "");
            } else {
                set(this.formData, name, value);
            }
        }
    }

    async setFieldValue(name, value) {
        set(this.formData, name, value);

        if(this.fieldNodes[name].isLit) {
            await this.fieldNodes[name].node.setFieldValue(value);
        }
    }

    handleRequestForValue(event) {
        const value = get(this.formData, event.detail.key, null);
        if(value) {
            event.detail.reply(value);
            event.stopPropagation();
        }
    }

    handleFieldRegister(event) {
        this.formDataTypes[event.detail.key] = event.detail.type;

        this.dispatchEvent(new CustomEvent(`form-field-register-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                key: event.detail.key,
                type: event.detail.type
            }
        }));
    }

    handleNodeRegister(event) {
        this.fieldNodes[event.detail.key] = event.detail.node;
    }

    handleFieldUpdate(event) {
        // field-update events from Children Lit Components
        const key = event.detail.key;
        const value = event.detail.value;

        set(this.formData, key, value);

        // to ui-stepper
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
        if(!isNil(event.detail.field)) {  // updated directly from lit element
            const this_field = event.detail.field;
            // get lit properties key,value
            const field = Object.fromEntries(
                [...this_field.constructor.elementProperties.keys()].map(k => [k, this_field[k]])
            );
            // updated directly from lit element - not via panel
            ActionOn(this.fieldNodes, field,
                    isArray(value) ? value[0] : value);
            Cascade(this, field,
                    event.detail.record ? event.detail.record : value);
        }
    }

    handleElementUpdate(element) {
        // non Lit components
        this.populateFormData(element, false);
    }

    handleFieldBlur(event) {
        // field-blur events from Children Lit Components
        // use timeout to allow onCancel to fire up if ever
        // TODO: find a better solution than setTimeout
        if(!isEmpty(this.fieldNodes)) {
            setTimeout(() => {
                const panel = this.shadowRoot.querySelector('form-panel');
                if(panel) panel.validate();
                else ValidateFields(this);
            }, 200);
        }
    }

    handleElementBlur(element) {
        // non Lit components
        // use timeout to allow onCancel to fire up if ever
        // TODO: find a better solution than setTimeout
        setTimeout(() => {
            ValidateFields(this);
        }, 200);
    }

    // local stepper
    onBack(event) {
        event.preventDefault();

        this.disableNextButton = false;
        this.activeStep -= 1;
    }

    // local stepper
    onNext(event) {
        event.preventDefault();

        const panel = this.shadowRoot.querySelector('form-panel');
        if(!panel.validate()) return false;
        panel.updateData();

        if(this.activeStep === (this.schemaPanels.length-1))  {
            this.onSubmit(event);
        } else {
            this.activeStep += 1;
            this.watermark = Math.max(this.watermark, this.activeStep);
        }
    }

    // local stepper
    onStep(step) {
        if(step === this.activeStep) return false;

        if(step <= this.watermark) {
            const panel = this.shadowRoot.querySelector('form-panel');
            if(!panel.validate()) return false;
            panel.updateData();

            this.activeStep = step;
        }
    }

    // ui-stepper parent
    handleStepperFocus() {
        if(isNil(this.dbTable)) {
            this.errorFocused = false;  // turn off validateFields focus
            Object.values(this.fieldNodes).forEach(obj => {
                if(obj.isLit) {
                    obj.node.focus();
                }
            });
        } else {
            const panel = this.shadowRoot.querySelector('form-panel');
            if(panel) panel.focus();
        }
    }

    // ui-stepper parent
    handleStepperBack(event, panel, stepperData, activeStep, totalSteps) {
        if(this.backHandler) {
            const myFunction = window[this.backHandler];
            if (isFunction(myFunction)) {
                return myFunction(event, panel, stepperData, mode, activeStep, totalSteps);
            }
        }
        return true;
    }

    // ui-stepper parent
    handleStepperNext(event, panel, stepperData, activeStep, totalSteps) {
        // Validate all fields before submitting the form
        if (this.validationSchema) {
            ValidateFields(this);
            if (Object.values(this.errors).some((error) => error)) {
                // There are errors
                return false;
            }
        } else {
            const form_panel = this.shadowRoot.querySelector('form-panel');
            if(form_panel) {
                if(!form_panel.validate()) return false;
            }
        }

        if(activeStep === totalSteps)  {
            if(this.submitHandler) {
                const myFunction = window[this.submitHandler];
                if (isFunction(myFunction)) {
                    return myFunction(event, this.formData);
                }
            }
        } else if(this.nextHandler) {
            const myFunction = window[this.nextHandler];
            if (isFunction(myFunction)) {
                return myFunction(event, panel, stepperData, activeStep, totalSteps);
            }
        }
        if(isEmpty(panel)) {
            for (const [key, value] of Object.entries(this.fieldNodes)) {
                let sender = event.detail.sender ? event.detail.sender : [];
                sender.push(`${this.instanceId}.handleStepperNext1`);
                this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: {
                        key: key,
                        value: get(this.formData, key, ""),
                        sender: sender
                    }
                }));
            }
        } else {
            if(Array.isArray(stepperData[panel])) {
                const list = [];
                for (const record of this.formData) {
                    list.push(record);
                }
                let sender = event.detail.sender ? event.detail.sender : [];
                sender.push(`${this.instanceId}.handleStepperNext2`);
                this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: {
                        key: panel,
                        value: list,
                        sender: sender
                    }
                }));
            } else {
                for (const [key, value] of Object.entries(this.fieldNodes)) {
                    let sender = event.detail.sender ? event.detail.sender : [];
                    sender.push(`${this.instanceId}.handleStepperNext3`);
                    this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                        bubbles: true,
                        composed: true,
                        detail: {
                            key: key,
                            value: get(this.formData, key, ""),
                            sender: sender
                        }
                    }));
                }
            }
        }
        return true;
    }

    // ui-stepper parent
    handleStepperStep(panel, step, stepperData, activeStep, totalSteps) {
        if(this.stepHandler) {
            const myFunction = window[this.stepHandler];
            if (isFunction(myFunction)) {
                return myFunction(panel, stepperData, activeStep, totalSteps);
            }
        }
        if(step > activeStep) {
            // validate if moving forward
            if (this.validationSchema) {
                ValidateFields(this);
                if (Object.values(this.errors).some((error) => error)) {
                    // There are errors
                    return false;
                }
            } else {
                const panel = this.shadowRoot.querySelector('form-panel');
                if(panel) return panel.validate();
            }
        }
        return true;
    }

    onCancel(event) {
        event.preventDefault();

        if(this.ownerCancelHandler) {
            this.dispatchEvent(new CustomEvent(`form-cancel-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: { value: this.formData }
            }));
            return false;
        }

        if(this.cancelHandler) {
            const myFunction = window[this.cancelHandler];
            if (isFunction(myFunction)) {
                return myFunction(event, this.formData);
            }
        }

        breadcrumbs.closePage();
    }

    handleSubmitButtonDisable(event) {
        if(this.isWizard && !isNull(this.nextButton)) {
            this.nextButton.disabled = event.detail.value;
            this.disableNextButton = event.detail.value;
            if(!isNil(event.detail.buttonText)) this.nextText = event.detail.buttonText;
            else this.nextText = this.nextOrigText;
        } else if(!isNull(this.submitButton)) {
            this.submitButton.disabled = event.detail.value;
        } else {
            // bubble up event to owner
            this.dispatchEvent(new CustomEvent(`submit-button-disable-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    value: event.detail.value,
                    buttonText: event.detail.buttonText
                }
            }));
        }
    }

    afterSubmitRefresh() {
        const toaster = document.querySelector("[data-toaster]");
        toaster.show("Refreshed","info");
    }

    async onSubmit(event) {
        event.preventDefault();

        if((!isNull(this.method) && this.method.toLowerCase() === "delete") ||
            this.mode === "Delete") {
            const deleteDialog = this.shadowRoot.querySelector("form-delete-dialog");
            deleteDialog.show();
            return false;
        }
        // Validate all fields before submitting the form
        if (this.validationSchema) {
            ValidateFields(this);
            if (Object.values(this.errors).some((error) => error)) {
                // There are errors
                return false;
            }
        } else {
            const panel = this.shadowRoot.querySelector('form-panel');
            if(panel && !panel.validate()) return false;
        }
        // convert form data to json data payload
        if(!isEmpty(this.formDataTypes)) {
            ConvertToJsonValues(this.formDataTypes, this.formData,
                store.get("user.Settings.Locale")[0],
                store.get("user.Settings.Timezone")[0]
            );
        }
        if(this.ownerSubmitHandler) {
            this.dispatchEvent(new CustomEvent(`form-submit-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    value: this.formData,
                    rowId: this.formData.Id,
                    type: this.formType,
                    mode: this.mode,
                    method: this.method
                }
            }));
            return false;
        }

        if(this.submitHandler) {
            const myFunction = window[this.submitHandler];
            if (isFunction(myFunction)) {
                return myFunction(event, this.formData);
            }
        }

        if(!isNull(this.method)) {
            const urlSearchParams = new URLSearchParams(this.formData).toString();
            try {
                switch(this.method.toLowerCase()) {
                    case "post":  // create
                        await api.POST(this.action, urlSearchParams)
                            .then(data => {
                                if(this.ownerSubmitPostPostHandler) {
                                    return this.dispatchEvent(new CustomEvent(`form-submit-post-post-${this.ownerId}`, {
                                        bubbles: true,
                                        composed: true,
                                        detail: {
                                            value: data,
                                            method: this.method,
                                            mode: this.mode
                                        }
                                    }));
                                } else if(this.submitPostPostHandler) {
                                    const myFunction = window[this.submitPostPostHandler];
                                    if (isFunction(myFunction)) {
                                        return myFunction(event, data);
                                    }
                                } else if(this.refreshAfterSubmit) {
                                    return this.afterSubmitRefresh();
                                }

                                breadcrumbs.closePage();
                            });
                        break;
                    case "put":   // update
                        await api.PUT(this.action, urlSearchParams)
                            .then(data => {
                                if(this.ownerSubmitPostPutHandler) {
                                    return this.dispatchEvent(new CustomEvent(`form-submit-post-put-${this.ownerId}`, {
                                        bubbles: true,
                                        composed: true,
                                        detail: {
                                            value: data,
                                            method: this.method,
                                            mode: this.mode
                                        }
                                    }));
                                } else if(this.submitPostPutHandler) {
                                    const myFunction = window[this.submitPostPutHandler];
                                    if (isFunction(myFunction)) {
                                        return myFunction(event, data);
                                    }
                                } else if(this.refreshAfterSubmit) {
                                    return this.afterSubmitRefresh();
                                }

                                breadcrumbs.closePage();
                            });
                }
            } catch (err) {
                console.log("form.onSubmit1 error:", err);
                const message = `form.onSubmit1 ${err.status} ${err.detail} : ${(this.title) ? this.title : this.action}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        } else if(!isNull(this.mode)) {
            const submitData = {
                "Depth": 1,
                "DbTableName": this.dbTable,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "RowId": this.mode === "Copy" ? 0 : this.rowId,
                "Schema": { "form_panels": this.schemaPanels,
                            "form_fields": this.schemaFields
                            },
                "Data": this.formData
            };
            if(this.parentTable) {
                submitData["ParentTable"] = this.parentTable;
                submitData["ParentField"] = this.parentField;
                submitData["ParentRowId"] = this.parentRowId;
                submitData["ParentRow"] = this.parentRow;
                submitData["join_list"] = this.joinList;
            }
            try {
                let url = null;
                switch(this.mode) {
                    case "Create":
                    case "Copy":
                        url = "/createTable";
                        if(this.parentTable) {
                            url = "/createChildTable";
                        }
                        await api.POST(url, submitData, "json")
                            .then(data => {
                                if(this.ownerSubmitPostPostHandler) {
                                    return this.dispatchEvent(new CustomEvent(`form-submit-post-post-${this.ownerId}`, {
                                        bubbles: true,
                                        composed: true,
                                        detail: {
                                            value: data,
                                            method: this.method,
                                            mode: this.mode
                                        }
                                    }));
                                } else if(this.submitPostPostHandler) {
                                    const myFunction = window[this.submitPostPostHandler];
                                    if (isFunction(myFunction)) {
                                        return myFunction(event, data);
                                    }
                                } else if(this.refreshAfterSubmit) {
                                    return this.afterSubmitRefresh();
                                }

                                breadcrumbs.closePage();
                            });
                        break;
                    case "Update":
                        url = "/updateTable";
                        if(this.parentTable) {
                            url = "/updateChildTable";
                        }
                        await api.PUT(url, submitData, "json")
                            .then(data => {
                                if(this.ownerSubmitPostPutHandler) {
                                    return this.dispatchEvent(new CustomEvent(`form-submit-post-put-${this.ownerId}`, {
                                        bubbles: true,
                                        composed: true,
                                        detail: {
                                            value: data,
                                            method: this.method,
                                            mode: this.mode
                                        }
                                    }));
                                } else if(this.submitPostPutHandler) {
                                    const myFunction = window[this.submitPostPutHandler];
                                    if (isFunction(myFunction)) {
                                        return myFunction(event, data);
                                    }
                                } else if(this.refreshAfterSubmit) {
                                    return this.afterSubmitRefresh();
                                }

                                breadcrumbs.closePage();
                            });
                }
            } catch (err) {
                console.log("form.onSubmit2 error:", err);
                const message = `form.onSubmit2 ${err.status}  ${err.detail}: ${(this.title) ? this.title : this.mode}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        }
    }

    async handleDeleteSubmit(event) {
        // convert form data to json data payload
        if(!isEmpty(this.formDataTypes)) {
            ConvertToJsonValues(this.formDataTypes, this.formData,
                store.get("user.Settings.Locale")[0],
                store.get("user.Settings.Timezone")[0]
            );
        }

        if(this.ownerSubmitHandler) {
            this.dispatchEvent(new CustomEvent(`form-submit-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    value: this.formData,
                    rowId: this.formData.Id,
                    type: this.formType,
                    mode: this.mode,
                    method: this.method
                }
            }));
            return false;
        }

        if(this.method) {
            const urlSearchParams = new URLSearchParams(this.formData).toString();
            try {
                await api.DELETE(this.action, urlSearchParams)
                    .then(data => {
                        if(this.ownerSubmitPostDeleteHandler) {
                            return this.dispatchEvent(new CustomEvent(`form-submit-post-delete-${this.ownerId}`, {
                                bubbles: true,
                                composed: true,
                                detail: {
                                    value: data,
                                    method: this.method,
                                    mode: this.mode
                                }
                            }));
                        } else if(this.submitPostDeleteHandler) {
                            const myFunction = window[this.submitPostDeleteHandler];
                            if (isFunction(myFunction)) {
                                    return myFunction(event, data);
                                }
                        } else if(this.refreshAfterSubmit) {
                            return this.afterSubmitRefresh();
                        }
                    });
                // close page without waiting for api return
                breadcrumbs.closePage();
            } catch (err) {
                console.log("form.handleDeleteSubmit1 error:", err);
                const message = `form.handleDeleteSubmit1 ${err.status} ${err.detail} : ${(this.title) ? this.title : this.action}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        } else if(this.mode) {
            const submitData = {
                "Depth": 1,
                "DbTableName": this.dbTable,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "RowId": this.rowId,
                "Schema": { "form_panels": this.schemaPanels,
                            "form_fields": this.schemaFields
                            },
                "Data": {"dummy": "dumb"}
            };
            if(this.parentTable) {
                submitData["ParentTable"] = this.parentTable;
                submitData["ParentField"] = this.parentField;
                submitData["ParentRowId"] = this.parentRowId;
                submitData["ParentRow"] = this.parentRow;
            }
            try {
                let url = "/deleteTable";
                if(this.parentTable) {
                    url = "/deleteChildTable";
                }
                await api.DELETE(url, submitData, "json")
                    .then(data => {
                        if(this.ownerSubmitPostDeleteHandler) {
                            return this.dispatchEvent(new CustomEvent(`form-submit-post-delete-${this.ownerId}`, {
                                bubbles: true,
                                composed: true,
                                detail: {
                                    value: data,
                                    method: this.method,
                                    mode: this.mode
                                }
                            }));
                        } else if(this.submitPostDeleteHandler) {
                            const myFunction = window[this.submitPostDeleteHandler];
                            if (isFunction(myFunction)) {
                                return myFunction(event, data);
                            }
                        } else if(this.refreshAfterSubmit) {
                            return this.afterSubmitRefresh();
                        }
                        breadcrumbs.closePage();
                    });
            } catch (err) {
                console.log("form.handleDeleteSubmit2 error:", err);
                const message = `form.handleDeleteSubmit2 ${err.status}  ${err.detail} : ${(this.title) ? this.title : this.mode}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        }
    }

    handleGridEvents(event) {
        if(!isEmpty(this.gridListeners)) {
            for (const obj of event.detail) {
                const listener = this.gridListeners.find(item => item.event === obj.event);
                if(listener) {
                    if(listener.field in this.fieldNodes) {
                        this.fieldNodes[listener.field].node.setFieldValue(obj.value);
                    }
                }
            }
        }
    }

    updated() {
        if(this.isWizard && isNull(this.nextButton)) {
            this.nextButton = this.shadowRoot.querySelector('[data-next]');
        } else if(isNull(this.submitButton)) {
            this.submitButton = this.shadowRoot.querySelector('button[type="submit"]');
        }
    }

    renderButtons() {
        if(this.isWizard) {
            let nextText = this.nextText;
            if(this.activeStep === (this.schemaPanels.length-1))  nextText = this.submitText;

            return html`
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
            `;
        }

        if(this.formButtons)
            return html`
                <button
                    @click="${this.onCancel}"
                    class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary">
                    ${this.cancelText}
                </button>
                <button type="submit"
                    @click="${this.onSubmit}"
                    class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary group-invalid:pointer-events-none group-invalid:opacity-30">
                    ${this.submitText}
                </button>
            `;

        if(this.formButtonCancel)
            return html`
                <button
                    @click="${this.onCancel}"
                    class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary">
                    ${this.cancelText}
                </button>
            `;

        if(this.formButtonSubmit)
            return html`
                <button type="submit"
                    @click="${this.onSubmit}"
                    class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary group-invalid:pointer-events-none group-invalid:opacity-30">
                    ${this.submitText}
                </button>
            `;
    }

    getData() {
        if(this.owner) return this.owner.getData();

        return this.formData;
    }

    reload() {
        // called by ui-step
        //this.requestUpdate();
        Object.keys(this.fieldNodes).forEach(name => {
            const node = this.fieldNodes[name];
            if(node.isLit) {
                node.node.reload();
            }
        });
    }

    shouldUpdate(changedProperties) {
        // check if can render
        return this.okToRender;
    }

    render() {
        const stepsTemplate = [];
        if(this.isWizard) {
            this.schemaPanels.forEach((panel, index) => {
                // To refer to hyphenated properties such as font-family,
                // use the camelCase equivalent (fontFamily) or
                // place the hyphenated property name in quotes ('font-family').
                let isOk = false;
                if(index < this.activeStep) isOk = true;
                else if(index <= this.watermark && !this.disableNextButton) isOk = true;

                const classes = {
                    "step-primary": index === this.activeStep ? true : false,
                    "cursor-pointer": isOk,
                };
                stepsTemplate.push(html`
                    <li class="step ${classMap(classes)}" @click="${() => this.onStep(index)}">${panel.desc || panel.label}</li>
                `);
            });
        }

        const cardTitle = FormTitle(this.title, this.stepperTitleFields, this.formData, this.keyTitle);

        return html`
            <div class="card w-full bg-base-100 shadow-xl group overflow-y-auto">
                <div class="card-body">
                    ${this.title ?
                        html`<h2 class="card-title">${cardTitle}</h2>`
                    : nothing}
                    ${this.isWizard ?
                        html`<ul class="steps steps-horizontal">
                            ${stepsTemplate}
                        </ul>`
                    : nothing}
                    ${this.dbTable ?
                        html`
                            <form-panel
                                ownerId="${this.instanceId}"
                                .owner="${this}"
                                mode="${this.mode}"
                                activeStep="${this.activeStep}"
                                program="${this.program}"
                                parentTable="${this.parentTable}"
                                parentField="${this.parentField}"
                                parentRowId="${this.parentRowId}"
                                .securityLevel='${this.securityLevel ? this.securityLevel : null}'
                                .schemaFields='${this.schemaFields ? this.schemaFields : null}'
                                .schemaPanels='${this.schemaPanels ? this.schemaPanels : null}'
                                .formData='${this.formData ? this.formData : null}'

                                .joinList='${this.joinList ? this.joinList : null}'
                                .parentRow='${this.parentRow ? this.parentRow : null}'

                                ?autoDefault="${this.autoDefault}"

                                .getGridSchemaHandler='${this.getGridSchemaHandler ? this.getGridSchemaHandler : null}'
                                .getGridDataHandler='${this.getGridDataHandler ? this.getGridDataHandler : null}'
                                .gridOptions='${this.gridOptions ? this.gridOptions : null}'
                            ></form-panel>`
                    :   html`<slot @slotchange="${this.onSlotChange}"></slot>`}
                    <div class="card-actions flex justify-end">
                        ${this.renderButtons()}
                    </div>
                </div>
            </div>
            <form-delete-dialog
                owner-id="${this.instanceId}"
                .owner="${this}"
            ></form-delete-dialog>
        `;
    }
}
customElements.define("ui-form", Form)


class FormDeleteDialog extends LitElement {
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
        title: { attribute: "delete-title", type: String },
        cancelText: { attribute: "cancel-text", type: String },
        submitText: { attribute: "submit-text", type: String },
    };

    constructor() {
        super();
        this.instanceId = (++FormDeleteDialog.instanceCounter).toString();

        this.owner = null;
        this.title = "DELETE this Record";
        this.cancelText = "Cancel";
        this.submitText = "Delete";
    }

    connectedCallback() {
        super.connectedCallback();

        this.instanceId = `FormDeleteDialog-${this.ownerId}-${this.instanceId}`;
    }

    onCancel(event) {
        this.dispatchEvent(new CustomEvent(`form-delete-cancel-${this.ownerId}`, {
            bubbles: true,
            composed: true
        }));
        const dialog = this.shadowRoot.querySelector("ui-dialog");
        dialog.closeModal();
    }

    onSubmit(event) {
        this.dispatchEvent(new CustomEvent(`form-delete-submit-${this.ownerId}`, {
            bubbles: true,
            composed: true
        }));
        const dialog = this.shadowRoot.querySelector("ui-dialog");
        dialog.closeModal();
    }

    show() {
        const dialog = this.shadowRoot.querySelector("ui-dialog");
        dialog.showModal();
    }

    render() {
        return html`
            <ui-dialog owner-id="${this.instanceId}" >
                <h3 class="font-bold text-lg">${this.title}</h3>
                <p class="py-4">Please confirm Record Deletion.</p>
                <div class="card-actions flex justify-end">
                    <button
                        @click="${this.onCancel}"
                        class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary">
                        ${this.cancelText}
                    </button>
                    <button
                        @click="${this.onSubmit}"
                        class="btn btn-primary rounded-sm w-fit focus:outline-none focus:ring focus:ring-primary group-invalid:pointer-events-none group-invalid:opacity-30">
                        ${this.submitText}
                    </button>
                </div>
            </ui-dialog>
        `;
    }
}
customElements.define("form-delete-dialog", FormDeleteDialog)
