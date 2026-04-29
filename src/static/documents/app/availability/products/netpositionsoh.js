import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../../css/tw.js'

import store from "../../../../js/store"
import api from "../../../../js/api"
import { isNull, isEmpty, get } from "../../../../js/utils"

class DocumentFGNetPositionSOH extends LitElement {
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

        styleId: { attribute: "style-id", type: Number },   // Product.Id
        colourId: { attribute: "colour-id", type: Number },  // Colour.Id
        fittingId: { attribute: "fitting-id", type: Number },  // Fitting.Id
        dimensionId: { attribute: "dimension-id", type: Number }, // Dimension.Id
        colFitDimId: { attribute: "colfitdim-id", type: Number },  // ProductColFitDim.Id
        warehouseIds: { attribute: "warehouse-ids", type: Array },  // Array of Warehouse.Id
    };

    constructor() {
        super();
        this.instanceId = "DocumentFGNetPositionSOH-" + (++DocumentFGNetPositionSOH.instanceCounter).toString();

        this.stockMovements = this.stockMovements.bind(this);
        this.stockMovementSchema = this.stockMovementSchema.bind(this);
        this.stockMovementData = this.stockMovementData.bind(this);
        this.getGridSchema = this.getGridSchema.bind(this);
        this.getGridData = this.getGridData.bind(this);

        // defaults
        this.ownerId = null;
        this.owner = null;

        this.styleId = null;
        this.colourId = null;
        this.fittingId = null;
        this.dimensionId = null;
        this.colFitDimId = null;
        this.warehouseIds = [];

        this.subTablesComponents = null;
        this.gridSchema = null;

        this.addEventListener(`grid-get-schema-${this.instanceId}`, this.stockMovementSchema);
        this.addEventListener(`grid-get-data-${this.instanceId}`, this.stockMovementData);
    }

    connectedCallback() {
        super.connectedCallback();

        this.subTablesComponents = [
            {"element": this.stockMovements, "title": "Stock Reconciliation"}
        ];

    }

    async getGridSchema() {
        const include_columns = [
            "Location.ItemWarehouseArea.ItemWarehouse.Warehouse",
            "Location.ItemWarehouseArea.Area",
            "Location.Location",
            "Location.Status",
            "Total"
        ];

        const params = {
            "TableName": "FGStocks",
            "ProductId": this.styleId
        };
        try {
            return await api.POST("/fgDrillDownSchema", params, null)
                .then(data => {
                    let columns = [];
                    for (const col of include_columns) {
                        const field = data.grid_fields.find(fld => fld.name === col);
                        if(field) {
                            field["options"] = {
                                    "sort": false,
                                    "sortDirection": "none",
                                    "display": field.visible,
                            };
                            columns.push(field);
                        }
                    }
                    data.grid_fields.forEach( field => {
                        let allow = false;
                        if(field.name >= "0" && field.name <= "99") {
                            allow = true;
                        }
                        if(allow) {
                            field["options"] = {
                                    "sort": false,
                                    "sortDirection": "none",
                                    "display": field.visible,
                            };
                            columns.push(field);
                        }
                    });
                    this.gridSchema =  {"grid_fields": columns,
                                        "grid_tables": data.grid_tables};
                    return this.gridSchema;
                });
        } catch (err) {
            console.log("netpositionSOH.getGridSchema error:", err);
            const message = `FGNetPosSOH.getGridSchema ${err.status}  ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    async getGridData(grid_columns, criteria, criteria_type, page, pagesize,
                      selectedRows, parentTable, parentField, parentRowId) {

        // op: 0 = EQUALS
        criteria.push({"field": "SKU.ItemColourFitDim.ItemProduct_Id", "op": 0,
                       "value": this.styleId });

        const params = {
            "CompanyRowId": store.get("user.Company_Id"),
            "ProductId": this.styleId,
            "ColourId": this.colourId,
            "FittingId": this.fittingId,
            "DimensionId": this.dimensionId,
            "ColFitDimId": this.colFitDimId,
            "WarehouseIds": this.warehouseIds,
            "Columns": this.gridSchema.grid_fields,
            "Criteria": criteria,
            "CriteriaType": criteria_type,
            "Offset": page,
            "PageSize": pagesize
        };

        try {
            return await api.POST("/fgDrillDownStock", params, null);
        } catch (err) {
            console.log("netpositionSOH.getGridData error:", err);
            const message = `DocumentFGNetPositionSOH.getGridSchema ${err.status}  ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    stockMovements(row) {
        const line = JSON.stringify(row).replace(/'/g, "&#39;"); // escape single quotes for JSON

        return `
            <ui-datatable
                owner-id="${this.instanceId}"
                grid-title="Stock Reconciliation"
                db-table="FGStockMovements"
                program="DocumentFGNetPositionSOH.FGStockMovements"

                input-data-select
                column-button
                refresh-button
                auto-refresh-button
                download-button
                print-button

                get-schema-event
                get-data-event

                parent-table="FGStocks"
                parent-row-id="${row.Id}"
                parent-row='${line}'

            ></ui-datatable>
        `;
    }

    async stockMovementSchema(event) {
        const include_columns = [
            "FromLocation.ItemWarehouseArea.ItemWarehouse.Warehouse",
            "FromLocation.ItemWarehouseArea.Area",
            "FromLocation.Location",
            "SKU.ItemColourFitDim.ItemProduct.Style",
            "SKU.ItemColourFitDim.ItemProduct.Name",
            "SKU.ItemColourFitDim.Colour.Colour",
            "SKU.ItemColourFitDim.Fitting.Fitting",
            "SKU.ItemColourFitDim.Dimension.Dimension",
            "SKU.Size.Size",
            "CreateTimeStamp",
            "Qty",
            "RunningBalance_Qty",
            "TotalCost",
            "RunningBalance_TotalCost",
            "Type",
            "Reason.Reason",
            "Document",
            "Reference",
            "Comments",
        ];

        try {
            const data = await api.GET("/gridSchema/FGStockMovements", null);
            let columns = [];
            let fld = null;
            for (const col of include_columns) {
                const field = data.grid_fields.find(fld => fld.name === col);
                if(field) {
                    field["options"] = {
                        "sort": false,
                        "sortDirection": "none",
                        "display": field.visible,
                    };
                    if(field.name === "SKU.ItemColourFitDim.ItemProduct.Style") {
                        field.label = "Style";
                        field.column_label = "Style";
                    } else if(field.name === "SKU.ItemColourFitDim.ItemProduct.Name") {
                        field.label = "Description";
                        field.column_label = "Description";
                    } else if(field.name === "CreateTimeStamp") {
                        field.label = "Date";
                        field.column_label = "Date";
                    } else if(field.name === "Qty") {
                        field.label = "Qty";
                        field.column_label = "Qty";
                    } else if(field.name === "RunningBalance_Qty") {
                        field.label = "Running Qty";
                        field.column_label = "Running Qty";
                    } else if(field.name === "TotalCost") {
                        field.label = "Cost";
                        field.column_label = "Cost";
                    } else if(field.name === "RunningBalance_TotalCost") {
                        field.label = "Running Cost";
                        field.column_label = "Running Cost";
                    }
                    columns.push(field);
                }
            }
            event.detail.resolve({"grid_fields": columns, "grid_tables": data.grid_tables});
        } catch (err) {
            event.detail.reject(err);
        }
    }

    async stockMovementData(event) {
        /* input-data-select should be defined otherwise event.detail.criteria is
           from the saved grid state
        */
        const crit = event.detail.criteria;
        const row = event.detail.parentRow;
        const whs =      get(row, "Location.ItemWarehouseArea.ItemWarehouse.Warehouse");
        const area =     get(row, "Location.ItemWarehouseArea.Area");
        const location = get(row, "Location.Location");
        // 0=EQUALS
        if(whs)
            crit.push({"field": "FromLocation.ItemWarehouseArea.ItemWarehouse.Warehouse",
                        "op": 0, "value": whs});
        if(area)
            crit.push({"field": "FromLocation.ItemWarehouseArea.Area",
                        "op": 0, "value": area});
        if(location)
            crit.push({"field": "FromLocation.Location",
                        "op": 0, "value": location});

        crit.push({"field": "SKU.ItemColourFitDim.ItemProduct_Id",
                        "op": 0, "value": this.styleId});
        if(this.colFitDimId) {
            crit.push({"field": "SKU.ItemColourFitDim_Id",
                        "op": 0, "value": this.colFitDimId});
        } else if(this.colourId) {
            crit.push({"field": "SKU.ItemColourFitDim.Colour_Id",
                        "op": 0, "value": this.colourId});
            if(this.fittingId) {
                crit.push({"field": "SKU.ItemColourFitDim.Fitting_Id",
                        "op": 0, "value": this.fittingId});
            }
            if(this.dimensionId) {
                crit.push({"field": "SKU.ItemColourFitDim.Dimension_Id",
                        "op": 0, "value": this.dimensionId});
            }
        }

        const params = {
            "CompanyRowId": store.get("user.Company_Id"),
            "Locale": store.get("user.Settings.Locale")[0],
            "Timezone": store.get("user.Settings.Timezone")[0],
            "FieldList": [],
            "DbTableName": "FGStockMovements",
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

    render() {
        return html`
            <ui-datatable
                owner-id="${this.instanceId}"
                grid-title="Stock On Hand"

                stateless
                column-button
                refresh-button
                auto-refresh-button
                download-button
                print-button

                .getGridSchemaHandler="${this.getGridSchema}"
                .getGridDataHandler="${this.getGridData}"
                .preSubTables="${this.subTablesComponents}"
            ></ui-datatable>
        `;
    }
}
customElements.define("ui-document-fgnetpositionsoh", DocumentFGNetPositionSOH)
