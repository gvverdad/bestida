import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../../css/tw.js'

import store from "../../../../js/store"
import api from   "../../../../js/api"
import { isNull, isEmpty } from "../../../../js/utils"

class DocumentFGNetPositionSO extends LitElement {
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

        styleId: { attribute: "style-id", type: Number },   // Style.Id
        colourId: { attribute: "colour-id", type: Number },  // Colour.Id
        fittingId: { attribute: "fitting-id", type: Number },  // Fitting.Id
        dimensionId: { attribute: "dimension-id", type: Number }, // Dimension.Id

        warehouseIds: { attribute: "warehouse-ids", type: Array },  // Array of Warehouse.Id

        status: { type: String },  // Order Status
    };

    constructor() {
        super();
        this.instanceId = "DocumentFGNetPositionSO-" + (++DocumentFGNetPositionSO.instanceCounter).toString();

        this.getGridSchema = this.getGridSchema.bind(this);
        this.getGridData = this.getGridData.bind(this);

        // defaults
        this.ownerId = null;
        this.owner = null;

        this.styleId = null;
        this.colourId = null;
        this.fittingId = null;
        this.dimensionId = null;
        this.warehouseIds = [];
        this.status = null;
    }

    connectedCallback() {
        super.connectedCallback();

    }

    async getGridSchema() {
        const include_columns = [
            "Warehouse.Warehouse",
            "ItemSalesOrderHeader.OrderNumber",
            "Line",
            "CreateTimeStamp",
            "ItemSalesOrderHeader.Customer.Account",
            "ItemSalesOrderHeader.Customer.Name",
            "ItemSalesOrderHeader.Store.Store",
            "ItemSalesOrderHeader.Store.Name"
        ];

        switch(this.status) {
            case "Allocated":
                include_columns.push("AllocatedTimeStamp");
                break;
            case "Packed":
                include_columns.push("PackedTimeStamp");
                break;
            case "Shipped":
                include_columns.push("Invoice.InvoiceNumber");
                include_columns.push("Invoice.CreateTimeStamp");
                break;
            case "Picked":
                include_columns.push("PickTicket.PTNumber");
                include_columns.push("PickTicket.CreateTimeStamp");
                break;
        }
        include_columns.push("Product.ItemProduct.Style");
        include_columns.push("Product.ItemProduct.Name");
        include_columns.push("Product.Colour.Colour");
        include_columns.push("Product.Fitting.Fitting");
        include_columns.push("Product.Dimension.Dimension");
        include_columns.push("Total");

        const params = {
            "TableName": "SalesOrderDetails",
            "ProductId": this.styleId,
        };
        try {
            return await api.POST("/fgDrillDownSchema", params, null)
                .then(data => {
                    let columns = [];
                    for (const col of include_columns) {
                        const field = data.grid_fields.find(fld => fld.name === col);
                        if(field) {
                            if(field.name === "ItemSalesOrderHeader.OrderNumber") {
                                field.label = "Order";
                                field.column_label = "Order";
                            } else if(field.name === "Line") {
                                field.label = "Line";
                                field.column_label = "Line";
                            } else if(field.name === "CreateTimeStamp") {
                                field.label = "Date";
                                field.column_label = "Date";
                            } else if(field.name === "ItemSalesOrderHeader.Customer.Account") {
                                field.label = "Account";
                                field.column_label = "Account";
                            } else if(field.name === "ItemSalesOrderHeader.Customer.Name") {
                                field.label = "Name";
                                field.column_label = "Name";
                            } else if(field.name === "ItemSalesOrderHeader.Store.Store") {
                                field.label = "Store";
                                field.column_label = "Store";
                            } else if(field.name === "ItemSalesOrderHeader.Store.Name") {
                                field.label = "Name";
                                field.column_label = "Name";
                            } else if(field.name === "Product.ItemProduct.Style") {
                                field.label = "Style";
                                field.column_label = "Style";
                            } else if(field.name === "Product.ItemProduct.Name") {
                                field.label = "Description";
                                field.column_label = "Description";
                            } else if(field.name === "Invoice.InvoiceNumber") {
                                field.label = "Invoice";
                                field.column_label = "Invoice";
                            } else if(field.name === "Invoice.CreateTimeStamp") {
                                field.label = "Invoiced";
                                field.column_label = "Invoiced";
                            } else if(field.name === "PickTicket.PTNumber") {
                                field.label = "Pick Ticket";
                                field.column_label = "Pick Ticket";
                            } else if(field.name === "PickTicket.CreateTimeStamp") {
                                field.label = "Picked";
                                field.column_label = "Picked";
                            } else if(field.name === "AllocatedTimeStamp") {
                                field.label = "Allocated";
                                field.column_label = "Allocated";
                            } else if(field.name === "PackedTimeStamp") {
                                field.label = "Packed";
                                field.column_label = "Packed";
                            }
                            field["options"] = {
                                    "sort": false,
                                    "sortDirection": "none",
                                    "display": field.visible,
                            };
                            columns.push(field);
                        }
                    }
                    data.grid_fields.forEach( field => {
                        if(field.name >= "0" && field.name <= "99") {
                            field["options"] = {
                                    "sort": false,
                                    "sortDirection": "none",
                                    "display": field.visible,
                            };
                            columns.push(field);
                        }
                    });
                    return {"grid_fields": columns,
                            "grid_tables": data.grid_tables};
                });
        } catch (err) {
            console.log("netpositionso.getGridSchema error:", err);
            const message = `DocumentFGNetPositionSO.getGridSchema ${err.status}  ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    async getGridData(grid_columns, criteria, criteria_type, page, pagesize,
                      selectedRows, parentTable, parentField, parentRowId) {

        const params = {
            "CompanyRowId": store.get("user.Company_Id"),
            "ProductId": this.styleId,
            "ColourId": this.colourId,
            "FittingId": this.fittingId,
            "DimensionId": this.dimensionId,
            "WarehouseIds": this.warehouseIds,
            "Status": this.status,
            "Offset": page,
            "PageSize": pagesize
        };
        try {
            return await api.POST("/fgDrillDownSalesOrder", params, null);
        } catch (err) {
            console.log("netpositionso.getGridData error:", err);
            const message = `DocumentFGNetPositionSO.getGridSchema ${err.status}  ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    render() {
        return html`
            <ui-datatable
                owner-id="${this.instanceId}"
                grid-title="${this.status}"
                db-table="SalesOrderDetails"

                stateless
                column-button
                refresh-button
                auto-refresh-button
                download-button
                print-button

                .getGridSchemaHandler="${this.getGridSchema}"
                .getGridDataHandler="${this.getGridData}"
            ></ui-datatable>
        `;
    }
}
customElements.define("ui-document-fgnetpositionso", DocumentFGNetPositionSO)
