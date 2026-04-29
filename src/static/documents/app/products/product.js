import { LitElement, html, css, nothing } from 'lit'
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { TWStyles } from '../../../css/tw.js'

import store from "../../../js/store"
import api from   "../../../js/api"
import { isEmpty } from "../../../js/utils"
import { createSubTables } from "../../../js/components/datatable/table"

class DocumentProduct extends LitElement {
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

        styleId: { type: Number },   // Product.Id
        style: { type: String },  // Style Code

        programStack: { attribute: "program-stack", type: Array },

        data: { state: true },
        okToRender: { state: true },
    };

    constructor() {
        super();
        this.instanceId = "DocumentProduct-" + (++DocumentProduct.instanceCounter).toString();

        // defaults
        this.ownerId = null;
        this.owner = null;

        this.styleId = null;
        this.style = null;

        this.data = null;
        this.image = null;
        this.description = null;

        this.okToRender = false;

        this.gridColumns= null;
        this.gridTables = null;
        this.dbTable = "Products";
        this.program = "DocumentProduct";
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
    }

    async connectedCallback() {
        super.connectedCallback();

        if(isEmpty(this.programStack))  this.programStack.push(this.program);

        const table_name = "Products";

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

        if(this.style) {
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
                    {"field": "Style", "op": 0, "value": this.style}
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
                "DbTableName": table_name,
                "RowId": this.styleId,
                "Mode": "Update",
                "TextAsString": true
            };
            await api.POST("/formData", params, "json")
                .then(data => {
                    this.data = data.data;
            });
        }

        let rec = this.data.Descriptions.find(ele => ele.DescriptionType.Type === "MAIN");
        if(rec) this.description = rec.Description;

        rec = this.data.Images.find(ele => ele.ImageType.Type === "MAIN");
        if(rec) this.image = `/images/${rec.File.split('/').pop()}`;  // get filename

        this.sub_tables = createSubTables(this.data, this.dbTable,
                               this.gridTables, this.gridColumns,
                               this.preSubTables, this.postSubTables,
                               this.tabSelect, this.program, this.instanceId,
                               this.securityLevel, this.gridFlags, this.gridOptions,
                               this.programStack);

        this.okToRender = true;
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
                            Style: ${this.data.Style}
                        </div>

                        <div class="text-base font-medium text-gray-700">
                            ${this.data.Name}
                        </div>

                        ${this.image ?
                            html`<div class="w-full h-[220px] bg-gray-300 rounded-lg flex items-center justify-center">
                                <span class="text-gray-600">
                                    <img
                                        src=${this.image}
                                        loading="lazy"
                                        alt="Product"
                                        class="
                                            rounded-lg
                                            object-contain
                                            w-full max-w-[400px]
                                            sm:w-[400px] sm:h-[400px]
                                        "
                                    />
                                </span>
                            </div>`
                        : nothing}

                        ${this.description ?
                            html`<p class="text-sm text-gray-600 leading-relaxed">
                                ${this.description}
                            </p>`
                        : nothing}

                    </div>

                    <div class="flex-1 bg-base-100 rounded-xl shadow p-4">
                        <div style="display:flex; flex-direction:column; gap:12px;">

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    UOM
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.UOM.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Season
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Season.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Gender
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Gender.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Brand
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Brand.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Category
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Category.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Fabric
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Fabric.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Product Class
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Class.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Product Type
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Type.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Product Group
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.Group.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Size Scale
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.SizeScale.Description}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Colour/Fit/Dims
                                </div>
                                <div style="flex:1; text-align:left;">
                                    ${this.data.number_of_colfitdims}
                                </div>
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Sample Style
                                </div>
                                ${this.data.Sample ?
                                    html`<div style="flex:1; text-align:left; color:green;">
                                        ✓
                                    </div>`
                                :   html`<div style="flex:1; text-align:left; color:red;">
                                        ✕
                                    </div>`
                                }
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Allow Sales
                                </div>
                                ${this.data.AllowSales ?
                                    html`<div style="flex:1; text-align:left; color:green;">
                                        ✓
                                    </div>`
                                :   html`<div style="flex:1; text-align:left; color:red;">
                                        ✕
                                    </div>`
                                }
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Allow Production
                                </div>
                                ${this.data.AllowProduction ?
                                    html`<div style="flex:1; text-align:left; color:green;">
                                        ✓
                                    </div>`
                                :   html`<div style="flex:1; text-align:left; color:red;">
                                        ✕
                                    </div>`
                                }
                            </div>

                            <div style="display:flex; gap:16px;">
                                <div style="width:144px; text-align:right; font-weight:600; flex-shrink:0;">
                                    Allow Purchasing
                                </div>
                                ${this.data.AllowPurchasing ?
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
customElements.define("ui-document-product", DocumentProduct)
