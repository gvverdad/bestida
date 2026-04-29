import { LitElement, html, css } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../css/tw.js'

import api from "../api"
import store from "../store"
import breadcrumbs from "../breadcrumb"
import { isNil, set, isNull, isEmpty } from "../utils"


class UploadImageForm extends LitElement {
    static styles = [css ``, TWStyles];

    static instanceCounter = 0;

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },

        title: { attribute: "upload-title", type: String },
        dbTable: { attribute: "table-name", type: String },
        fileField: { attribute: "file-fieldname", type: String },
        mimeField: { attribute: "mime-fieldname", type: String },

        mode: { type: String }, // Create, Copy, Update, Delete
        localData: { attribute: "local-data", type: Boolean },
        rowId: { attribute: "row-id", type: Number },
        formType: { attribute: "form-type", type: String },
        formData: { attribute: "initial-values", type: Object },

        program: { type: String },
        // security to pass to child components ie. datatables
        securityLevel: { attribute: "security-level", type: Object },
        // use form buttons - Stepper has buttons too
        formButtons: { attribute: "form-buttons", type: Boolean },
        // cancel button text, default to Cancel
        cancelText: { attribute: "cancel-text", type: String },
        // submit button text, default to Submit
        submitText: { attribute: "submit-text", type: String },

        ownerCancelHandler: { attribute: "owner-cancel-handler", type: Boolean },
        ownerSubmitHandler: { attribute: "owner-submit-handler", type: Boolean },
        ownerSubmitPostPutHandler: { attribute: "owner-submit-post-put-handler", type: Boolean },
        ownerSubmitPostDeleteHandler: { attribute: "owner-submit-post-delete-handler", type: Boolean },
        ownerSubmitPostPostHandler: { attribute: "owner-submit-post-post-handler", type: Boolean },

        refreshAfterSubmit: { attribute: "refresh-after-submit", type: Boolean },
        submitPostPutHandler: { attribute: "submit-post-put-handler", type: String },
        submitPostDeleteHandler: { attribute: "submit-post-delete-handler", type: String },
        submitPostPostHandler: { attribute: "submit-post-post-handler", type: String },

        parentTable: { attribute: "parent-table", type: String },
        parentField: { attribute: "parent-field", type: String },
        parentRowId: { attribute: "parent-row-id", type: Number },
        parentRow: { attribute: "parent-row", type: Object },
        joinList: { attribute: "join-list", type: Array },

        schema: { state: true }
    };

    constructor() {
        super();

        this.instanceId = "UploadImageForm-" + (++UploadImageForm.instanceCounter).toString();

        // bind the event listener to reference the component instance
        this.getSchema = this.getSchema.bind(this);
        this.handleFormData = this.handleFormData.bind(this);
        this.handleFieldUpdate = this.handleFieldUpdate.bind(this);
        this.handleFormSubmit = this.handleFormSubmit.bind(this);
        this.handleFormCancel = this.handleFormCancel.bind(this);

        this.title = null;
        this.dbTable = null;
        this.fileField = "File";
        this.mimeField = "MimeType";
        this.mode = "Create";
        this.localData = false;
        this.formType = null;

        this.program = null;
        this.securityLevel = {
            "runLevel": 999,
            "createLevel": 999,
            "updateLevel": 999,
            "deleteLevel": 999
        };
        this.formButtons = false;
        this.cancelText = "Cancel";
        this.submitText = "Submit";

        this.ownerCancelHandler = false;
        this.ownerSubmitHandler = false;
        this.ownerSubmitPostPutHandler = false;
        this.ownerSubmitPostPostHandler = false;
        this.ownerSubmitPostDeleteHandler = false;

        this.refreshAfterSubmit = false;
        this.submitPostPutHandler = null;
        this.submitPostDeleteHandler = null;
        this.submitPostPostHandler = null;

        this.parentTable = null;
        this.parentField = null;
        this.parentRowId = 0;
        this.parentRow = null;
        this.joinList = null;

        this.schema = null;
        this.rowId = 0;
        this.formData = {};

        this.addEventListener(`form-field-updated-${this.instanceId}`, this.handleFieldUpdate);
        this.addEventListener(`form-submit-${this.instanceId}`, this.handleFormSubmit);
        this.addEventListener(`form-cancel-${this.instanceId}`, this.handleFormCancel);
        this.addEventListener(`form-data-${this.instanceId}`, this.handleFormData);
    }

    async connectedCallback() {
        super.connectedCallback();

        await api.GET(`/formSchema/${this.dbTable}`, null).then(data => {
            const schemaFields = [];
            data.form_fields.forEach(field => {
                if(field.name === this.fileField) {
                    field["label"] = "Image File";
                    field["type"] = "File";
                }
                else if(field.name === this.mimeField) {
                    field["modifiable"] = false;
                }
                field["options"] = {
                    "sort": false,
                    "sortDirection": "none",
                    "display": field.displayable,
                    "modifiable": field.modifiable
                };
                schemaFields.push(field);
            });

            this.schema = {
                "form_panels": data.form_panels,
                "form_fields": schemaFields
            };
        });
    }

    getSchema() {
        return this.schema;
    }

    handleFormData(event) {
        this.formData = event.detail.value;
    }

    handleFieldUpdate(event) {
        // field-update events from Children Lit Components
        const key = event.detail.key;
        const value = event.detail.value;

        if(key === this.fileField) {
            set(this.formData, key, value.filenames[0]);
            if(this.mimeField) set(this.formData, this.mimeField, value.formats[0]);
        } else {
            set(this.formData, key, value);
        }
    }

    handleFormCancel(event) {
        if(this.ownerCancelHandler) {
            this.dispatchEvent(new CustomEvent(`form-cancel-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: { value: this.formData }
            }));
            return false;
        }

        breadcrumbs.closePage();
    }

    async handleFormSubmit(event) {

        if(this.ownerSubmitHandler) {
            this.dispatchEvent(new CustomEvent(`form-submit-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    value: this.formData,
                    rowId: this.formData.Id,
                    type: this.formType,
                    mode: this.mode
                }
            }));
            return false;
        }

        const submitData = {
            "Depth": 1,
            "DbTableName": this.dbTable,
            "CompanyRowId": store.get("user.Company_Id"),
            "Locale": store.get("user.Settings.Locale")[0],
            "Timezone": store.get("user.Settings.Timezone")[0],
            "RowId": this.rowId,
            "Schema": this.schema,
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
                    url = "/createTable";
                    if(this.parentTable) {
                        url = "/createChildTable";
                    }
                    await api.POST(url, submitData, "json").then(data => {
                        if(this.ownerSubmitPostPostHandler) {
                            return this.dispatchEvent(new CustomEvent(`form-submit-post-post-${this.ownerId}`, {
                                bubbles: true,
                                composed: true,
                                detail: {
                                    value: data,
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
                    await api.PUT(url, submitData, "json").then(data => {
                        if(this.ownerSubmitPostPutHandler) {
                            return this.dispatchEvent(new CustomEvent(`form-submit-post-put-${this.ownerId}`, {
                                bubbles: true,
                                composed: true,
                                detail: {
                                    value: data,
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
                console.log("uploadImage.handleFormSubmit error:", err);
                const message = `uploadImage.handleFormSubmit ${err.status}  ${err.detail}: ${(this.title) ? this.title : this.mode}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
        }
    }

    shouldUpdate(changedProperties) {
        // check if can render
        if(isEmpty(this.schema)) return false;
        return true;
    }

    render() {
        let mode_name = null;
        switch(this.mode) {
            case "Update":
                mode_name = "Update";
                break;
            case "Delete":
                mode_name = "Delete";
                break;
            default:
                mode_name = "Upload";
        }
        let title = this.title || `${mode_name} ${this.schema.form_panels[0].label}`;
        return html`
            <ui-form
                owner-id="${this.instanceId}"
                mode="${this.mode}"
                form-title="${title}"
                db-table="${this.dbTable}"
                row-id="${this.rowId}"
                form-type="${this.formType}"
                program="${this.program}"

                ?form-buttons="${this.formButtons}"
                ?local-data="${this.localData}"
                ?owner-cancel-handler="${this.ownerCancelHandler}"
                owner-submit-handler
                ?owner-submit-post-post-handler="${this.ownerSubmitPostPostHandler}"

                submit-text="${this.submitText}"

                parent-table="${this.parentTable}"
                parent-field="${this.parentField}"
                parent-row-id="${this.parentRowId}"
                .parentRow="${this.parentRow}"
                .joinList="${this.joinList}"

                .securityLevel="${this.securityLevel}"

                .formData='${this.formData ? this.formData : null}'
                .getFormSchemaHandler="${this.getSchema}"
            >
            </ui-form>
        `;
    }
}

customElements.define("ui-uploadimageform", UploadImageForm)
