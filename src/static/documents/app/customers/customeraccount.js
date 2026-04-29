import { LitElement, html, css, nothing } from 'lit'
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { TWStyles } from '../../../css/tw.js'

import store from "../../../js/store"
import api from   "../../../js/api"
import { isEmpty } from "../../../js/utils"
import { createSubTables, formatCell } from "../../../js/components/datatable/table"

class DocumentCustomerAccount extends LitElement {
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
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },

        accountId: { type: Number },   // Customer.Id
        account: { type: String },  // Customer.Account

        programStack: { attribute: "program-stack", type: Array },

        data: { state: true },
        okToRender: { state: true },
    };

    constructor() {
        super();
        this.instanceId = "DocumentCustomerAccount-" + (++DocumentCustomerAccount.instanceCounter).toString();

        // bind the event listener to reference the component instance

        // defaults
        this.ownerId = null;
        this.owner = null;

        this.accountId = null;
        this.account = null;

        this.data = null;
        this.address = null;
        this.phone = null;
        this.email = null;
        this.contact = null;

        this.okToRender = false;

        this.gridColumns= null;
        this.gridTables = null;
        this.dbTable = "Customers";
        this.program = "DocumentCustomerAccount";
        this.preSubTables = null;
        this.postSubTables = null;
        this.tabSelect = 0;
        this.gridOptions = null;
        this.gridFlags = {
            localData: false,
            uploadImageButton: false,
            addButton: false,
            copyButton: false,
            updateButton: false,
            deleteButton: false,
            filterButton: true,
            columnButton: true,
            refreshButton: true,
            downloadButton: true,
            printButton: true
        };
        this.securityLevel = {
            "runLevel": 0,         // can run viewers
            "createLevel": 99999,  // cannot create
            "updateLevel": 99999,  // cannot modify
            "deleteLevel": 99999   // cannot delete
        };

        this.sub_tables = null;
        this.programStack = [];

        this.addEventListener(`grid-get-data-${this.instanceId}`, this.getStockGridData);
    }

    async connectedCallback() {
        super.connectedCallback();

        if(isEmpty(this.programStack))  this.programStack.push(this.program);

        await api.GET(`/gridSchema/${this.dbTable}`, null).then(data => {
            this.gridTables = data.grid_tables;
            data.grid_fields.forEach( field => {
                field["options"] = {
                    "sort": false,
                    "sortDirection": "none",
                    "display": field.visible,
                    "modifiable": field.modifiable
                };
            });
            this.gridColumns = data.grid_fields;
        });

        let crit = [{"field": "Id", "op": 0, "value": this.accountId}];
        if(this.account) crit = [{"field": "Account", "op": 0, "value": this.account}];

        const params = {
            "Depth": 1,
            "CompanyRowId": store.get("user.Company_Id"),
            "Locale": store.get("user.Settings.Locale")[0],
            "Timezone": store.get("user.Settings.Timezone")[0],
            "FieldList": [],
            "DbTableName": this.dbTable,
            "Criteria": crit,
            "CriteriaType": 0, // ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3
            "Columns": [], // this.gridColumns,
            "Offset": 0,
            "PageSize": 1,
            "ChoicesAsTuple": false,
            "ChoicesKey": true,
            "TextAsString": true,
            "Draw": 1,
            "SelectedRows": []
        };

        // use /list instead of /formData or /formDataCriteria
        // need to m2m merge Brands and Keywords
        await api.POST("/list", params, "json").then(data => {
            this.data = data.data[0]; // first record
        });
console.log("DocumentCustomerAccont:", params, this.data);
        let rec = this.data.Addresses.find(ele => ele.Type.Type === "MAIN");
        if(rec) {
            this.address = rec.Line1;
            if(!isEmpty(rec.Line2)) this.address += "<br />" + rec.Line2;
            this.address += "<br />" + rec.Locality.Name;
            this.address += " " + rec.State.StateCode;
            this.address += " " + rec.Postcode.Postcode;
            this.address += "<br />" + rec.Country;
        }

        rec = this.data.Phones.find(ele => ele.Type.Type === "MAIN");
        if(rec) this.phone = rec.Phone;

        rec = this.data.Emails.find(ele => ele.Type.Type === "MAIN");
        if(rec) this.email = rec.Email;

        rec = this.data.Contacts.find(ele => ele.Type.Type === "MAIN");
        if(rec) this.contact = rec.first_last_name;

        this.sub_tables = createSubTables(this.data, this.dbTable,
                               this.gridTables, this.gridColumns,
                               this.preSubTables, this.postSubTables,
                               this.tabSelect, this.program, this.instanceId,
                               this.securityLevel, this.gridFlags, this.gridOptions,
                               this.programStack);
        this.okToRender = true;
    }

    formatField(name) {
        const field = this.gridColumns.find(col => col.name === name);
        return formatCell(this.data, field, true, true, false);
    }

    shouldUpdate(changedProperties) {
        // check if can render
        return this.okToRender;
    }

    render() {
        return html`
            <div class="w-full h-full flex flex-col bg-base-200">

                <div class="flex flex-row gap-4 p-4">
                    <div class="flex-1 bg-base-100 rounded-xl shadow p-4 flex flex-col gap-4">

                        <div class="text-lg font-bold">
                            Account: ${this.data.Account}
                        </div>

                        <div class="text-base font-medium text-gray-700">
                            ${this.data.Name}
                        </div>

                        <div class="space-y-2 text-sm">

                            <!-- Address -->
                            ${this.address ?
                                html`<div class="flex gap-2">
                                    <span class="font-semibold">Address:</span>
                                    <span class="leading-snug">
                                        ${unsafeHTML(this.address)}
                                    </span>
                                </div>`
                            : nothing }

                            ${this.phone ?
                                html`<div class="flex gap-2">
                                    <span class="font-semibold">Phone:</span>
                                    <span>${this.phone}</span>
                                </div>`
                            : nothing }

                            ${this.email ?
                                html`<div class="flex gap-2">
                                    <span class="font-semibold">Email:</span>
                                    <span>${this.email}</span>
                                </div>`
                            : nothing }

                            ${this.contact ?
                                html`<div class="flex gap-2">
                                    <span class="font-semibold">Contact:</span>
                                    <span>${this.contact}</span>
                                </div>`
                            : nothing }
                        </div>
                    </div>

                    <div class="flex-1 bg-base-100 rounded-xl shadow p-4">
                        <div style="display:flex; flex-direction:column; gap:12px;">

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Brands
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Brands.Description")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Region
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Region.Description")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Type
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Type.Description")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Class
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Class.Description")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Group
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Group.Description")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Price Band
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("PriceBand.Description")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Priority
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Priority.Description")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Preferred Carrier
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Carrier.Name")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Shipment Percentage
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("ShipmentPercentage")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Ship From Warehouse
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("ShipFromWarehouse.Warehouse")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Order/Start Date Interval Days
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("OrderDateInterval")}                                    
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Start/Cancel Date Interval Days
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("StartDateInterval")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Locale
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Locale")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Timezone
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Timezone")}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Allow Deliveries
                                </div>
                                ${this.formatField("AllowDeliveries")}
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Inactive
                                </div>
                                ${this.formatField("Inactive")}
                            </div>

                           <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Inter Company
                                </div>
                               ${this.formatField("InterCompany")}
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:250px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Keywords
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.formatField("Keywords.Keyword")}
                                </div>
                            </div>
                            
                        </div>
                    </div>
                </div>

                ${this.sub_tables ?
                    html`<div class="flex-1 p-4">
                            <div class="w-full h-full bg-base-100 rounded-xl shadow flex flex-col">
                                ${unsafeHTML(this.sub_tables)}
                            </div>
                        </div>`
                : nothing }
            </div>
        `;
    }
}
customElements.define("ui-document-customeraccount", DocumentCustomerAccount)
