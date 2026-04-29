import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../css/tw.js'

import store from "../../../js/store"
import api from   "../../../js/api"
import { isEmpty } from "../../../js/utils"

class DocumentInvoice extends LitElement {
    static styles = [
        css `
            :host{
                display: block;
            }
        `,
        TWStyles
    ];

    static instanceCounter = 0;

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },

        invoiceId: { type: Number },   // SalesOrderInvoice.Id
        invoiceNumber: { type: Number },  // SalesOrderInvoice.InvoiceNumber

        data: { state: true },
    };

    constructor() {
        super();
        this.instanceId = "DocumentInvoice-" + (++DocumentInvoice.instanceCounter).toString();

        // defaults
        this.ownerId = null;
        this.owner = null;

        this.invoiceId = null;
        this.invoiceNumber = null;

        this.schemaFields = null;
        this.schemaPanels = null;

        this.data = null;
    }

    async connectedCallback() {
        super.connectedCallback();

        const table_name = "SalesOrderInvoices";

        await api.GET(`/formSchema/${table_name}`, null).then(data => {
            this.schemaPanels = data.form_panels;
            this.schemaFields = data.form_fields;
        });

        if(this.invoiceNumber) {
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
                "DbTableName": table_name,
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "InvoiceNumber", "op": 0, "value": this.invoiceNumber}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.data = data.data;
            });
        } else if(this.invoiceId) {
            const params = {
                "Depth": 1,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "FieldList": [],
                "DbTableName": table_name,
                "RowId": this.invoiceId,
                "Mode": "Update",
                "TextAsString": true
            };
            await api.POST("/formData", params, "json")
                .then(data => {
                    this.data = data.data;
            });
        }
    }

    shouldUpdate(changedProperties) {
        // check if can render
        if(isEmpty(this.data)) return false;
        else return true;
    }

    render() {
        return html`
            <div>Hello Invoice ${this.data.InvoiceNumber}</div>
        `;
    }
}
customElements.define("ui-document-invoice", DocumentInvoice)
