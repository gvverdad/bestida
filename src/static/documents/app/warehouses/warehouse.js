import { LitElement, html, css, nothing } from 'lit'
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { TWStyles } from '../../../css/tw.js'

import store from "../../../js/store"
import api from   "../../../js/api"
import { isEmpty } from "../../../js/utils"
import { createSubTables } from "../../../js/components/datatable/table"

class DocumentWarehouse extends LitElement {
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

        warehouseId: { type: Number },   // Warehouse.Id
        warehouse: { type: String },  // Warehouse Code

        programStack: { attribute: "program-stack", type: Array },

        data: { state: true },
        okToRender: { state: true },
    };

    constructor() {
        super();
        this.instanceId = "DocumentWarehouse-" + (++DocumentWarehouse.instanceCounter).toString();

        // bind the event listener to reference the component instance
        this.getStockGridData = this.getStockGridData.bind(this);
        this.drillDownStocks = this.drillDownStocks.bind(this);

        // defaults
        this.ownerId = null;
        this.owner = null;

        this.warehouseId = null;
        this.warehouse = null;

        this.data = null;
        this.address = null;
        this.phone = null;
        this.email = null;
        this.contact = null;

        this.okToRender = false;

        this.gridColumns= null;
        this.gridTables = null;
        this.dbTable = "Warehouses";
        this.program = "DocumentWarehouse";
        this.preSubTables = null;
        this.postSubTables = [
            {"element": this.drillDownStocks, "title": "Stocks",
             "program": "DocumentWarehouse.ProductStockOnHand" }
        ];
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

        if(this.warehouse) {
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
                "DbTableName": this.dbTable,
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "Warehouse", "op": 0, "value": this.warehouse}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.data = data.data;
            });
        } else {
            const params = {
                "Depth": 1,
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "FieldList": [],
                "DbTableName": this.dbTable,
                "RowId": this.warehouseId,
                "Mode": "Update",
                "TextAsString": true
            };
            await api.POST("/formData", params, "json")
                .then(data => {
                    this.data = data.data;
            });
        }

        let rec = this.data.Addresses.find(ele => ele.Type.Type === "MAIN");
        if(rec) {
            this.address = rec.Line1;
            if(!isEmpty(rec.Line2)) this.address += "<br />" + rec.Line2;
            this.address += "<br />" + rec.Locality.Name;
            this.address += " " + rec.State.StateCode;
            this.address += " " + rec.Postcode.Postcode;
            this.address += "<br />" + rec.Country[1];
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

    async getStockGridData(event) {
        /* input-data-select should be defined otherwise event.detail.criteria is
           from the saved grid state
        */
        const crit = event.detail.criteria;
        // op: 0 = EQUALS
        crit.push({"field": "Location.ItemWarehouseArea.ItemWarehouse_Id", "op": 0,
                   "value": this.data.Id });

        const params = {
            "CompanyRowId": store.get("user.Company_Id"),
            "Locale": store.get("user.Settings.Locale")[0],
            "Timezone": store.get("user.Settings.Timezone")[0],
            "FieldList": [],
            "DbTableName": "FGStocks",
            "Criteria": crit,
            "CriteriaType": event.detail.criteriaType, // ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3
            "Columns": event.detail.gridColumns,
            "Offset": event.detail.page * (event.detail.pagesize > 0 ? event.detail.pagesize : 0),
            "PageSize": event.detail.pagesize,
            "ChoicesAsTuple": false,
            "ChoicesKey": true,
            "TextAsString": true,
            "Draw": 1,
        };
        try {
            const result = await api.POST("/list", params, "json");
            event.detail.resolve(result);
        } catch (err) {
            event.detail.reject(err);
        }

    }

    drillDownStocks() {
        return `
            <ui-datatable
                owner-id="${this.instanceId}"
                grid-title="Product Stock On Hand"
                db-table="FGStocks"
                program="DocumentWarehouse.ProductStockOnHand"
                program-stack='${JSON.stringify(this.programStack)}'

                filter-button
                column-button
                refresh-button
                download-button
                print-button

                input-data-select
                get-data-event
            ></ui-datatable>
        `;
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
                            Warehouse: ${this.data.Warehouse}
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
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Type
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Type}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Status
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Status}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Areas
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.number_of_areas}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Inactive
                                </div>
                                ${this.data.Inactive ?
                                    html`<div style="flex:1; text-align:left; color:green;">
                                        ✓
                                    </div>`
                                :   html`<div style="flex:1; text-align:left; color:red;">
                                        ✕
                                    </div>`
                                }
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
customElements.define("ui-document-warehouse", DocumentWarehouse)
