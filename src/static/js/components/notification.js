import { LitElement, html, css } from 'lit'
import { TWStyles } from '../../css/tw.js'

import api from "../api"
import store from "../store"
import { isEmpty } from "../utils"
import { navigateTo } from "../router"

import "../../icons/eyes.js"
import "../../icons/check.js"


class Notification extends LitElement {
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
        this.instanceId = "Notification-" + (++Notification.instanceCounter).toString();

        // bind the event listener to reference the component instance - this
        this.viewFileTool = this.viewFileTool.bind(this);
        this.viewFile = this.viewFile.bind(this);
        this.readAllTool = this.readAllTool.bind(this);
        this.readAll = this.readAll.bind(this);
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
        const data = await api.GET("/notificationgridschema", null);
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
        return api.POST("/notificationdata", params, "json");
    }

    getFormSchema() {
        return api.GET("/notificationformschema", null);
    }

    updateForm(container, data, table) {
        this.grid = table;  // datatable "this" context

        const component = document.createElement("ui-form");
        component.ownerId = this.instanceId;
        component.title = "Update Notification";
        component.dbTable = "Notifications";
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
        component.getSchemaHandler = this.getFormSchema;

        container.addElement(component);
    }

    handleFormCancel(event) {
        if(this.grid) this.grid.toggleCollapse();
    }

    handlePostSubmitPut(event) {
        // refresh indicator
        myNotifications.getNotifications();
        if(this.grid) this.grid.handleFormClose(event);
    }

    viewFile() {
        if(isEmpty(this.selectedRow)) return false;

        const uri = "/spoolviewer/" + encodeURIComponent(this.selectedRow.SpoolTitle) + "/" + encodeURIComponent(this.selectedRow.SpoolFile);
        navigateTo(uri);
    }

    viewFileTool(rowSelected) {
        if(rowSelected)
            return html`<div class="tooltip tooltip-bottom z-[10]"
                                data-tip="View Notification Attachment">
                            <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.viewFile}">
                                    <icon-eyes></icon-eyes>
                            </button>
                   </div>`;
        else return html``;
    }

    async readAll() {
        const grid = this.shadowRoot.querySelector("ui-datatable");
        if(grid) {
            await api.PUT("/notificationsreadall", null, "json");
            grid.getGridData("info", "All notifications flagged as read");  // refresh grid
        }
        // refresh indicator
        myNotifications.getNotifications();
    }

    readAllTool() {
        return html`
            <div class="tooltip tooltip-bottom z-[10]" data-tip="Flag All as Read">
                <button class="btn btn-ghost rounded-full"
                    style="padding: 8px; height: inherit; min-height: inherit;"
                    @click="${this.readAll}">
                    <icon-check></icon-check>
                </button>
            </div>`;
    }

    render() {
        const tools = [
            (rowSelected) => this.viewFileTool(rowSelected),
            () => this.readAllTool()
        ];

        return html`
            <ui-datatable
                owner-id="${this.instanceId}"
                grid-title="Notifications"
                db-table="Notifications"
                program="Notifications"

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
customElements.define("ui-notification", Notification)

class MyNotifications {
    constructor() {
        this.viewNotification = this.viewNotification.bind(this);

        this.timerId = null;
        this.notifications = [];

        // milliseconds
        // TODO: make this a config option
        this.refreshInterval = 900000; // 15 minutes * 60 seconds = 900 * 1000
    }

    enable() {
        if(this.timerId) {
            this.disable();
        }
        this.getNotifications();

        // use arrow function to maintain 'this' context
        this.timerId = setInterval(() => { this.getNotifications(); },
                            this.refreshInterval);
    }

    disable() {
       if(this.timerId) {
            clearInterval(this.timerId);

            this.timerId = null;
            this.notifications = [];
        }
    }

    async viewNotification(event) {
        event.preventDefault();

        let target = event.target;
        if(target.tagName !== "A") {
            while (target && target !== document) {
                if (target.tagName === 'A') {
                    // Found an <a> element
                    break;
                }
                target = target.parentNode;
            }
        }
        // close dropdown
        target.blur();
        // view Notification
        navigateTo(target.href);
        // close Notification record
        const item = this.notifications.find(obj => obj.Id === parseInt(target.dataset.id));
        if(item) {
            try {
                await this.closeNotificationItem(item);
                this.getNotifications();
            } catch (err) {
                const message = `notification.viewNotification ${err.status}  ${err.detail}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        }
    }

    closeNotificationItem(item) {
        item.Read = true;
        const data = {
                "Depth": 1,
                "DbTableName": "Notifications",
                "CompanyRowId": store.get("user.Company_Id"),
                "Locale": store.get("user.Settings.Locale")[0],
                "Timezone": store.get("user.Settings.Timezone")[0],
                "RowId": item.Id,
                "Data": item
        };
        return api.PUT("/updateTable", data, "json");
    }


    async getNotifications() {
        const totals = document.querySelector("[data-totalMyNotifications]");
        const list = document.querySelector("[data-myNotificationsList]");

        const locale = store.get("user.Settings.Locale")[0];
        const timezone = store.get("user.Settings.Timezone")[0];

        this.notifications = [];
        try {
            await api.GET("/mynotifications", null).then(data => {
                if(data.data) this.notifications = data.data;
                if(totals) {
                    totals.innerHTML = "";
                    if(this.notifications.length > 0) {
                        const len = this.notifications.length > 99 ? "99+" : this.notifications.length;
                        totals.innerHTML = `
                            <span class="indicator-item badge badge-secondary text-white z-[25]">${len}</span>
                        `;
                    }
                }
                if(list) {
                    list.innerHTML = "";
                    if(this.notifications.length > 0) {
                        const ul = document.createElement("ul");
                        ul.setAttribute("tabindex", "0");
                        ul.className = `block dropdown-content z-[99] menu p-2 shadow bg-base-200 text-base-content rounded-box w-max`;

                        this.notifications.forEach(item => {
                            const li = document.createElement("li");
                            const a = document.createElement("a");
                            a.setAttribute("data-link", true);
                            a.setAttribute("data-id", item.Id);
                            a.addEventListener("click", this.viewNotification);
                            a.addEventListener("blur", this.closeNotifications);
                            const createdate = new Intl.DateTimeFormat(locale,
                                    { timeZone: timezone, dateStyle: "medium", timeStyle: "short" })
                                    .format(new Date(item.CreateTimeStamp));
                            a.href = "/spoolviewer/" + encodeURIComponent(item.Title) + "/" + encodeURIComponent(item.SpoolFile);
                            a.innerHTML = `
                                <article class="prose">
                                    <h4 class="m-0">${item.Title}</h4>
                                    <p class="m-0">${item.Text}</p>
                                    <p class="m-0">${createdate}</p>
                                </article>
                            `;
                            li.appendChild(a);
                            ul.appendChild(li);
                        });
                        list.appendChild(ul);
                    }
                }
            });
        } catch (err) {
            const message = `notification.getNotifications ${err.status}  ${err.detail}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }
}
export const myNotifications = new MyNotifications();
