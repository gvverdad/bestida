import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../../css/tw.js'

import store from "../../../../js/store"
import api from   "../../../../js/api"
import { isNull, isEmpty } from "../../../../js/utils"

class DocumentFGNetPosition extends LitElement {
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

        styleId: { type: Number },   // Product.Id
        colourId: { type: Number },  // Colour.Id
        fittingId: { type: Number },  // Fitting.Id
        dimensionId: { type: Number }, // Dimension.Id
        colFitDimId: { type: Number },  // ProductColFitDim.Id
        warehouseIds: { type: Array },  // Array of Warehouse.Id
        areaId: { type: Number },  // WarehouseArea.Id
        locationId: { type: Number },  // WarehouseLocation.Id

        style: { type: String },  // Style Code
        colour: { type: String }, // Colour Code
        fitting: { type: String }, // Fitting Code
        dimension: { type: String }, // Dimension Code
        warehouse: { type: String }, // Warehouse code
        area: { type: String }, // Area code
        location: { type: String }, // Location code

        programStack: { attribute: "program-stack", type: Array },

        data: { state: true },
    };

    constructor() {
        super();
        this.instanceId = "DocumentFGNetPosition-" + (++DocumentFGNetPosition.instanceCounter).toString();

        // bind the event listener to reference the component instance
        this.getGridSchema = this.getGridSchema.bind(this);
        this.getGridData = this.getGridData.bind(this);
        this.setBold = this.setBold.bind(this);
        this.drillDownComponent = this.drillDownComponent.bind(this);

        this.program = "DocumentFGNetPosition";

        // defaults
        this.ownerId = null;
        this.owner = null;

        this.styleId = null;
        this.colourId = null;
        this.fittingId = null;
        this.dimensionId = null;
        this.colFitDimId = null;
        this.warehouseIds = [];
        this.areaId = null;
        this.locationId = null;

        this.style = null;
        this.colour = null;
        this.fitting = null;
        this.dimension = null;
        this.warehouse = null;
        this.area = null;
        this.location = null;

        this.data = null;
        this.subTablesComponents = null;
        this.programStack = [];
    }

    async connectedCallback() {
        super.connectedCallback();

        if(isEmpty(this.programStack))  this.programStack.push(this.program);

        this.subTablesComponents = [
            {"element": this.drillDownComponent, "title": "Drill Down"}
        ];

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
                "DbTableName": "Products",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "Style", "op": 0, "value": this.style}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.styleId = data.data.Id;
            });
        }

        if(this.colour) {
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
                "DbTableName": "Colours",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "Colour", "op": 0, "value": this.colour}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.colourId = data.data.Id;
            });
        }

        if(this.fitting) {
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
                "DbTableName": "Fittings",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "Fitting", "op": 0, "value": this.fitting}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.fittingId = data.data.Id;
            });
        }

        if(this.dimension) {
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
                "DbTableName": "Dimensions",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "Dimension", "op": 0, "value": this.dimension}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.dimensionId = data.data.Id;
            });
        }

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
                "DbTableName": "Warehouses",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "Warehouse", "op": 0, "value": this.warehouse}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.warehouseIds = [data.data.Id];
            });
        }

        if(this.warehouse && this.area) {
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
                "DbTableName": "WarehouseAreas",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "ItemWarehouse.Warehouse", "op": 0, "value": this.warehouse},
                    {"field": "Area", "op": 0, "value": this.area}
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.areaId = data.data.Id;
            });
        }

        if(this.warehouse && this.area && this.location) {
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
                "DbTableName": "WarehouseLocations",
                "Criteria": [
                    // op: 0 = EQUALS
                    {"field": "ItemWarehouseArea.ItemWarehouse.Warehouse", "op": 0, "value": this.warehouse},
                    {"field": "ItemWarehouseArea.Area", "op": 0, "value": this.area},
                    {"field": "Location", "op": 0, "value": this.location},
                ]
            };
            await api.POST("/formDataCriteria", params, "json")
                .then(data => {
                    this.locationId = data.data.Id;
            });
        }


        if(this.colourId === 0)  this.colourId = null;
        if(this.fittingId === 0)  this.fittingId = null;
        if(this.dimensionId === 0)  this.dimensionId = null;
        if(this.areaId === 0)  this.areaId = null;
        if(this.locationId === 0)  this.locationId = null;

        if(!isNull(this.styleId)) {
            this.getNPSchema();
        }
    }

    async getNPSchema() {
        const params = {
            "CompanyRowId": store.get("user.Company_Id"),
            "ProductId": this.styleId,
            "ColourId":  this.colourId,
            "FittingId": this.fittingId,
            "DimensionId": this.dimensionId,
            "ColFitDimId": this.colFitDimId,
            "WarehouseIds": this.warehouseIds,
            "AreaId": this.areaId,
            "LocationId": this.locationId
        };
        try {
            await api.POST("/fgNetPosition", params, "json")
                .then(data => {
                    this.data = data;
                });
        } catch (err) {
            console.log("DocumentFGNetPosition.getNPSchema error:", err);
            const message = `DocumentFGNetPosition.getNPSchema ${err.status}  ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    async getGridSchema() {
        if(isNull(this.data)) {
            await this.getNPSchema();
        }

        const table = "NetPosition";
        const grid_table = [{
            "table": table,
            "label": "Net Position",
            "desc": "Net Position"}
        ];

        const header = this.data.NetPosition.slice(0, 1)
        const columns = [];
        header[0].forEach((field, idx) => {
            columns.push({
                "name": idx.toString(),
                "field_name": idx.toString(),
                "label": field,
                "column_label": field,
                "table": table,
                "type": (idx > 0 ? "Integer" : "String"),
                "length": (idx > 0 ? 0 : 64),
                "decimal": 0,
                "sortable": false,
                "visible": true,
                "modifiable": false,
                "options": {
                                "sort": false,
                                "sortDirection": "none",
                                "display": true,
                            },
                "cell_function": this.setBold
            });
        });
        return {"grid_fields": columns, "grid_tables": grid_table};
    }

    setBold(row, column, value=null, asString=true) {
        if(["Stock On Hand","UnShipped","Stock Availability","Free To Sell","Projected Availability"].includes(row["0"])) {
            return `<span class="font-bold">${value}</span>`;
        }
        return value;
    }

    async getGridData() {
        if(isNull(this.data)) {
            await this.getNPSchema();
        }

        const records = this.data.NetPosition.slice(1)
        const position_data = [];
        records.forEach( (row, ldx) => {
            const line = {};
            line["Id"] = ldx+1; // unique id for line selection
            row.forEach( (ele, idx) => {
                line[idx.toString()] = ele;
            });
            position_data.push(line);
        });

        return {
            draw: 1,
            data: position_data,
            recordsTotal: position_data.length
        };
    }

    drillDownComponent(row) {
        const title = row["0"]

        const props = {
            "styleId": this.styleId,
            "colourId": this.colourId ? this.colourId : null,
            "fittingId": this.fittingId ? this.fittingId : null,
            "dimensionId": this.dimensionId ? this.dimensionId : null,
            "colFitDimId": this.colFitDimId ? this.colFitDimId : null,
            "warehouseIds": this.warehouseIds,
            "status": title
        }

        switch(title) {
            case "Stock On Hand":
                return `
                    <ui-document
                        owner-id="${this.instanceId}"
                        program="DocumentFGNetPositionSOH"
                        params='${JSON.stringify(props)}'
                    ></ui-document>
                `;
            case "Booked":
                return `
                    <ui-document
                        owner-id="${this.instanceId}"
                        program="DocumentFGNetPositionSO"
                        params='${JSON.stringify(props)}'
                    ></ui-document>
                `;
            case "Shipped":
                return `
                    <ui-document
                        owner-id="${this.instanceId}"
                        program="DocumentFGNetPositionSO"
                        params='${JSON.stringify(props)}'
                    ></ui-document>
                `;
            case "UnShipped":
                return `
                    <ui-document
                        owner-id="${this.instanceId}"
                        program="DocumentFGNetPositionSO"
                        params='${JSON.stringify(props)}'
                    ></ui-document>
                `;
            case "Allocated":
                return `
                    <ui-document
                        owner-id="${this.instanceId}"
                        program="DocumentFGNetPositionSO"
                        params='${JSON.stringify(props)}'
                    ></ui-document>
                `;
            case "Picked":
                return `
                    <ui-document
                        owner-id="${this.instanceId}"
                        program="DocumentFGNetPositionSO"
                        params='${JSON.stringify(props)}'
                    ></ui-document>
                `;
            case "Packed":
                return `
                    <ui-document
                        owner-id="${this.instanceId}"
                        program="DocumentFGNetPositionSO"
                        params='${JSON.stringify(props)}'
                    ></ui-document>
                `;
            case "Planned PO":
                return this.genericComponent(title, "TODO");
            case "Outstanding PO":
                return this.genericComponent(title, "TODO");
            case "Projected Availability":
                return this.genericComponent(title, "TODO");
            default:
                return this.genericComponent(title, "This page intentionally left blanks");
        }
    }

    genericComponent(title, message) {
        return `
            <div class="card w-full bg-base-100 shadow-xl overflow-y-auto">
                <div class="navbar bg-base-100 flex justify-between items-center">
                    <div class="flex items-center gap-x-5">
                        <h2 class="card-title">${title}</h2>
                    </div>
                </div>
                <div class="card-body" style="padding-top: 5px; padding-bottom: 10px;">
                    <div class="block w-full overflow-auto">
                        <div class="flex justify-center">${message}</div>
                    </div>
                </div>
            </div>
        `;
    }

    // setData from parent components ie: ui-step non fetch-data
    setData(data) {
        this.styleId = data.Style ? data.Style.Id : null;
        this.colourId = data.Colour ? data.Colour.Id : null;
        this.fittingId = data.Fitting ? data.Fitting.Id : null;
        this.dimensionId = data.Dimension ? data.Dimension.Id : null;

        this.warehouseIds = [];
        data.Warehouses.forEach(whs => {
            this.warehouseIds.push(whs.Id);
        });

        this.data = null;
        this.getNPSchema();
    }

    // called by ui-step - fetch-data ui-step
    reload() {
        this.data = null;
        this.getNPSchema();
    }

    render() {
        return html`
            ${this.data ?
                html`<ui-datatable
                    owner-id="${this.instanceId}"
                    grid-title="Net Position"

                    refresh-button
                    auto-refresh-button
                    download-button
                    print-button

                    stateless

                    .getGridDataHandler="${this.getGridData}"
                    .getGridSchemaHandler="${this.getGridSchema}"
                    .preSubTables="${this.subTablesComponents}"

                    grid-options='{"footer": false}'
                    ></ui-datatable>`
            : nothing }
        `;
    }
}
customElements.define("ui-document-fgnetposition", DocumentFGNetPosition)
