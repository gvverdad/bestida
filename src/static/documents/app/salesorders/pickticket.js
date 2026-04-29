import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../css/tw.js'

import store from "../../../js/store"
import api from   "../../../js/api"
import { isEmpty } from "../../../js/utils"

class DocumentPickTicket extends LitElement {
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

        ptId: { type: Number },   // SalesOrderPickTicket.Id
        ptNumber: { type: Number },  // SalesOrderPickTicket.PTNumber

        data: { state: true },
    };

    constructor() {
        super();
        this.instanceId = "DocumentPickTicket-" + (++DocumentPickTicket.instanceCounter).toString();

        // defaults
        this.ownerId = null;
        this.owner = null;

        this.ptId = null;
        this.ptNumber = null;

        this.schemaFields = null;
        this.schemaPanels = null;

        this.data = null;
    }

    async connectedCallback() {
        super.connectedCallback();

        const table_name = "SalesOrderPickTickets";

        await api.GET(`/formSchema/${table_name}`, null).then(data => {
            this.schemaPanels = data.form_panels;
            this.schemaFields = data.form_fields;
        });

        if(this.ptNumber) {
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
                    {"field": "PTNumber", "op": 0, "value": this.ptNumber}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.data = data.data;
            });
        } else if(this.ptId) {
            const params = {
                "Depth": 1,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "FieldList": [],
                "DbTableName": table_name,
                "RowId": this.ptId,
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
            <div>Hello PT ${this.data.PTNumber}</div>
        `;
    }
}
customElements.define("ui-document-pickticket", DocumentPickTicket)
