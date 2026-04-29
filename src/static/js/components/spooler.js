import { LitElement, html, css } from 'lit'
import { TWStyles } from '../../css/tw.js'

import api from "../api"
import store from "../store"
import { isEmpty } from "../utils"
import { navigateTo } from "../router"

import "../../icons/eyes.js"

class Spooler extends LitElement {
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
    }

    constructor() {
        super();
        this.instanceId = "Spooler-" + (++Spooler.instanceCounter).toString();

        // bind the event listener to reference the component instance - this
        this.pageViewerTool = this.pageViewerTool.bind(this);
        this.viewFile = this.viewFile.bind(this);
        this.handleSelectedRow = this.handleSelectedRow.bind(this);
        this.updateForm = this.updateForm.bind(this);
        this.handlePostSubmitPut = this.handlePostSubmitPut.bind(this);
        this.handleFormCancel = this.handleFormCancel.bind(this);

        this.grid = null;  // datatable "this" context

        this.selectedRow = null;

        this.addEventListener(`grid-select-row-${this.instanceId}`, this.handleSelectedRow);
        this.addEventListener(`form-cancel-${this.instanceId}`, this.handleFormCancel);
        this.addEventListener(`form-submit-post-put-${this.instanceId}`, this.handlePostSubmitPut);
    }

    handleSelectedRow(event) {
        this.selectedRow = event.detail.value;
    }

    async getGridSchema() {
        const data = await api.GET("/spoolergridschema", null);
        let grid_fields = [];
        data.grid_fields.forEach( field => {
            field["options"] = {
                "sort": false,
                "sortDirection": "none",
                "display": field.visible,
                "modifiable": false
            };
            grid_fields.push(field);
        });
        return {"grid_fields": grid_fields,
                "grid_tables": data.grid_tables};
    }

    getGridData(grid_columns, criteria, criteria_type, page, pagesize, selected_rows) {
        const params = {
                    "Depth": 1,
                    "CompanyRowId": store.get("user.Company_Id"),
                    "Locale": store.get("user.Settings.Locale")[0],
                    "Timezone": store.get("user.Settings.Timezone")[0],
                    "FieldList": [],
                    "DbTableName": "Spoolers",
                    "Criteria": criteria,
                    "CriteriaType": criteria_type, // ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3
                    "Columns": grid_columns,
                    "Offset": page * (pagesize > 0 ? pagesize : 0),
                    "PageSize": pagesize,
                    "ChoicesAsTuple": false,
                    "ChoicesKey": true,
                    "TextAsString": true,
                    "Draw": 1,
                    "SelectedRows": selected_rows
        };
        return api.POST("/spoolerdata", params, "json");
    }

    getFormSchema() {
        return api.GET("/spoolerformschema", null);
    }

    updateForm(container, data, table) {
        this.grid = table;  // datatable "this" context

        const component = document.createElement("ui-form");
        component.ownerId = this.instanceId;
        component.title = "Update Spool";
        component.dbTable = "Spoolers";
        component.rowId = data.Id;
        component.formData = data;
        component.mode = "Update";
        component.formButtons = true;
        component.submitText = "Update";
        component.parentTable = table.parentTable;
        component.parentField = table.parentField;
        component.parentRowId = table.parentRowId;
        component.parentRow = table.parentRow;
        component.joinList = table.joinList;
        component.program = `${table.program}.Spoolers`;
        component.securityLevel = table.securityLevel;
        component.ownerCancelHandler = true;
        component.ownerSubmitPostPutHandler = true;
        component.getFormSchemaHandler = this.getFormSchema;

        container.addElement(component);
    }

    handleFormCancel(event) {
        if(this.grid) this.grid.toggleCollapse();
    }

    handlePostSubmitPut(event) {
        if(this.grid) this.grid.handleFormClose(event);
    }

    viewFile() {
        if(isEmpty(this.selectedRow)) return false;

        const uri = "/spoolviewer/" + encodeURIComponent(this.selectedRow.Title) + "/" + encodeURIComponent(this.selectedRow.File);
        navigateTo(uri);
    }

    pageViewerTool(rowSelected) {
        if(rowSelected)
            return html`<div class="tooltip tooltip-bottom z-[10]" data-tip="View Spool">
                            <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.viewFile}">
                                    <icon-eyes></icon-eyes>
                            </button>
                   </div>`;
        else return html``;
    }

    render() {
        const tools = [
            (rowSelected) => this.pageViewerTool(rowSelected)
        ];

        return html`
            <ui-datatable
                owner-id="${this.instanceId}"
                grid-title="Spooler"
                db-table="Spoolers"
                program="Spoolers"

                select-row
                update-button delete-button filter-button
                column-button refresh-button auto-refresh-button
                download-button print-button

                .prependToolbar="${tools}"
                .getGridDataHandler="${this.getGridData}"
                .getGridSchemaHandler="${this.getGridSchema}"
                .updateForm="${this.updateForm}"
            ></ui-datatable>
        `;
    }
}
customElements.define("ui-spooler", Spooler)
