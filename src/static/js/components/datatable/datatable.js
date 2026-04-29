import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../css/tw.js'

import api from "../../api"
import { menu } from "../../menu"
import store from "../../store"
import { navigateTo } from "../../router"
import { isNil, isNull, isArray, isFunction, isEmpty, get, set, criteriaOps2Int } from "../../utils"

import "./header"
import "./table"
import "./footer"
import "./columns"
import "./filter"
import "./refresh"

class Datatable extends LitElement {
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
        // this grid is a component of owner (Form or Stepper)
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },
        // if a component of form - name is required
        name: { type: String },   // datatable as a form component

        title: { attribute: "grid-title", type: String },
        label: { type: String },  // form label
        // will build grid based on dbTable properties
        dbTable: { attribute: "db-table", type: String },
        // level of table data/schema query
        tableLevel: { attribute: "table-level", type: Number },
        // rows
        gridData: { attribute: "grid-data", type: Array },

        // get data using this server url
        getGridDataURL: { attribute: "get-data-url", type: String },   // GET
        postGridDataURL: { attribute: "post-data-url", type: String }, // POST
        // use Event to getGridData from parent
        getGridDataEvent: { attribute: "get-data-event", type: Boolean },
        // call parent getGridData directly
        getGridDataHandler: { type: Function },

        // get schema using this server url
        getGridSchemaURL: { attribute: "get-schema-url", type: String },
        // use Event to getGridSchema from parent
        getGridSchemaEvent: { attribute: "get-schema-event", type: Boolean },
        // call parent getGridSchema directly
        getGridSchemaHandler: { type: Function },

        // used to save this state in ProgramStates
        program: { type: String },
        gridOptions: { attribute: "grid-options", type: Object },
        securityLevel: { attribute: "security-level", type: Object },
        // used to get children using api datasource listChild
        parentTable: { attribute: "parent-table", type: String },
        parentField: { attribute: "parent-field", type: String },
        parentRowId: { attribute: "parent-row-id", type: Number },
        parentRow: { attribute: "parent-row", type: Object },
        joinList: { attribute: "join-list", type: Array },

        // addition Field Criteria
        getGridDataFilter: { attribute: "get-data-filter", type: Array },

        // Stepper Next Button Text when no row selected
        nextButtonText: { attribute: "next-button-text", type: String },
        // Stepper Next Button Text when a row is selected
        selectButtonText: { attribute: "next-button-select-text", type: String },
        // for validation (Stepper Next or Form validateFields)
        min: { type: Number },  // minimum selection
        max: { type: Number },  // maximum selection
        validator_messages: { attribute: "validator-messages", type: Array },


        // in HTML, boolean attributes are dictated by whether they are present or not,
        // not by the string value
        // therefore if "multiple" exists in HTML then multiSelect = true
        // else multiSelect defaults to false in ctor

        toolbar: { type: Boolean },
        footbar: { attribute: "footer", type: Boolean },
        // allow multiple selection - defaults to one row selection
        multiSelect: { attribute: "multiple", type: Boolean },
        // gridData is local data - dont update db
        localData: { attribute: "local-data", type: Boolean },
        // throw selected row to whoever is interested to catch
        selectRow: { attribute: "select-row", type: Boolean },
        // input data from form is to populate selectedRows
        inputDataSelect: { attribute: "input-data-select", type: Boolean },
        // input data from form is to populate grid data
        inputDataGrid: { attribute: "input-data-grid", type: Boolean },
        // return form mode. "Create" when NO row is selected otherwise "Update"
        formMode: { attribute: "form-mode", type: Boolean },
        // Stepper Next Button disabled - depending on validation (Next Button) as opposed to form validation
        activeNextButton: { attribute: "active-next-button", type: Boolean },

        // default grid header group buttons
        uploadImageButton: { attribute: "upload-image-button", type: Boolean },
        addButton: { attribute: "add-button", type: Boolean },
        copyButton: { attribute: "copy-button", type: Boolean },
        updateButton: { attribute: "update-button", type: Boolean },
        deleteButton: { attribute: "delete-button", type: Boolean },
        filterButton: { attribute: "filter-button", type: Boolean },
        columnButton: { attribute: "column-button", type: Boolean },
        bookmarkButton: { attribute: "bookmark-button", type: Boolean },
        refreshButton: { attribute: "refresh-button", type: Boolean },
        autoRefreshButton: { attribute: "auto-refresh-button", type: Boolean },
        downloadButton: { attribute: "download-button", type: Boolean },
        printButton: { attribute: "print-button", type: Boolean },
        viewerButton: { attribute: "viewer-button", type: Boolean },

        // get/save ProgramStates
        stateless: { type: Boolean },

        // additional grid header buttons
        // placed before grid header default buttons group
        prependToolbar: { type: Array },
        // placed after grid header default buttons group
        appendToolbar: { type: Array },

        // additional subTables
        // placed before gridTables subTables
        preubTables: { type: Array },
        // placed after gridTables subTables
        postSubTables: { type: Array },

        programStack: { attribute: "program-stack", type: Array },

        // server side javascript override functions
        postSubmitHandler: { attribute: "post-submit-handler", type: String },
        nextHandler: { attribute: "next-handler", type: String },
        backHandler: { attribute: "back-handler", type: String },
        stepHandler: { attribute: "step-handler", type: String },
        addFormString: { attribute: "add-form", type: String },
        copyFormString: { attribute: "copy-form", type: String },
        updateFormString: { attribute: "update-form", type: String },
        deleteFormString: { attribute: "delete-form", type: String },

        // parent override functions
        parentNextHandler: { type: Function },
        parentBackHandler: { type: Function },
        parentStepHandler: { type: Function },
        addForm: { type: Function },
        copyForm: { type: Function },
        updateForm: { type: Function },
        deleteForm: { type: Function },

        // footer data
        totalRows: { state: true },
        rowsPerPage: { state: true },
        currentPage: { state: true },

        // api model tableSchema
        // grid columns properties
        gridColumns: { state: true },
        // grid column tables properties
        gridTables: { state: true },

        // grid filters
        criteria: { state: true },
        // type of filter - ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3
        criteriaType: { state: true },

        // auto refresh settings
        autoRefresh: { state: true },
        refreshInterval: { state: true },

        // selected Rows
        selectedRows: { state: true },
        // parent Rows opened displaying child rows
        openRows: { state: true },

        // current grid crud mode - Create/Copy/Update/Delete
        // to control header crud buttons display
        crudMode: { state: true },

        // for multiple selection is the Select All checkbox button checked
        allRowsSelected: { state: true },
        // grid error message text - populated and enabled by form validation
        errorMessage: { state: true }, // error message property from parent form
    };

    constructor() {
        super();
        this.instanceId = "Datatable-" + (++Datatable.instanceCounter).toString();

        this.handleRowsPerPageChange = this.handleRowsPerPageChange.bind(this);
        this.handlePageChange = this.handlePageChange.bind(this);
        this.handleSelectAll = this.handleSelectAll.bind(this);
        this.handleUploadImage = this.handleUploadImage.bind(this);
        this.handleViewer = this.handleViewer.bind(this);
        this.handleAdd = this.handleAdd.bind(this);
        this.handleCopy = this.handleCopy.bind(this);
        this.handleUpdate = this.handleUpdate.bind(this);
        this.handleDelete = this.handleDelete.bind(this);
        this.handleFilter = this.handleFilter.bind(this);
        this.handleApplyFilter = this.handleApplyFilter.bind(this);
        this.handleColumns = this.handleColumns.bind(this);
        this.handleColumnsUpdate = this.handleColumnsUpdate.bind(this);
        this.handleBookmark = this.handleBookmark.bind(this);
        this.handleBookmarkUpdate = this.handleBookmarkUpdate.bind(this);
        this.handleRefresh = this.handleRefresh.bind(this);
        this.handleAutoRefresh = this.handleAutoRefresh.bind(this);
        this.handleApplyAutoRefresh = this.handleApplyAutoRefresh.bind(this);
        this.handleCopyClipboard = this.handleCopyClipboard.bind(this);
        this.handleDownloadPDF = this.handleDownloadPDF.bind(this);
        this.handleDownloadExcel = this.handleDownloadExcel.bind(this);
        this.handleDownloadCsv = this.handleDownloadCsv.bind(this);
        this.handlePrint = this.handlePrint.bind(this);
        this.handleChildGridUpdate = this.handleChildGridUpdate.bind(this);

        this.handleFormSubmit = this.handleFormSubmit.bind(this);
        this.handleFormClose = this.handleFormClose.bind(this);

        this.handleRowSelected = this.handleRowSelected.bind(this);
        this.handleRowOpened = this.handleRowOpened.bind(this);
        this.handleTabSelect = this.handleTabSelect.bind(this);
        this.handleSortColumn = this.handleSortColumn.bind(this);
        this.handleDropColumn = this.handleDropColumn.bind(this);

        this.handleStepperBack = this.handleStepperBack.bind(this);
        this.handleStepperNext = this.handleStepperNext.bind(this);
        this.handleStepperStep = this.handleStepperStep.bind(this);

        this.ownerId = null;
        this.owner = null;
        this.title = null;
        this.label = null;
        this.dbTable = null;
        this.tableLevel = 1;
        this.program = null;
        this.programStack = [];
        this.programRecord = null;
        this.toolbar = true;
        this.footbar = true;

        this.crudMode = null;
        this.startRow = 0,
        this.rowsPerPage = 10,
        this.currentPage = 1,

        this.gridColumns = null;
        this.gridTables = null;
        this.gridData = [];

        this.getGridDataURL = null;
        this.postGridDataURL = null;
        this.getGridDataEvent = false;
        this.getGridDataHandler = null;

        this.getGridSchemaURL = null;
        this.getGridSchemaEvent = false;
        this.getGridSchemaHandler = null;

        this.totalRows = 0,
        this.localData = false;

        this.getGridDataFilter = [];

        this.nextButtonText = null;
        this.selectButtonText = null;
        this.activeNextButton = false;
        this.selectRow = false;
        this.inputDataSelect = false;
        this.inputDataGrid = false;

        this.formMode = false;

        this.bookmarked = false;
        this.uploadImageButton = false;
        this.addButton = false;
        this.copyButton = false;
        this.updateButton = false;
        this.deleteButton = false;
        this.filterButton = false;
        this.columnButton = false;
        this.bookmarkButton = false;
        this.refreshButton = false;
        this.autoRefreshButton = false;
        this.downloadButton = false;
        this.printButton = false;
        this.viewerButton = false;
        this.stateless = false;

        this.addButtonInit = null;
        this.copyButtonInit = null;
        this.updateButtonInit = null;
        this.deleteButtonInit = null;

        this.criteria = [];
        this.criteriaType = 0; // ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3

        this.autoRefresh = false;
        this.refreshInterval = 60;  // 60 seconds
        this.timerId = null;

        this.selectedRows = [];
        this.openRows = [];
        this.allRowsSelected = false;
        this.multiSelect = false;
        this.tabSelect = 0;

        this.prependToolbar = [];
        this.appendToolbar = [];

        this.preSubTables = [];
        this.postSubTables = [];

        this.table = null;
        this.columns = null;
        this.collapse = null;
        this.header = null;
        this.footer = null;

        this.securityLevel = {
            "runLevel": 999,
            "createLevel": 999,
            "updateLevel": 999,
            "deleteLevel": 999
        };

        this.gridOptions = null;

        this.parentTable = null;
        this.parentField = null;
        this.parentRowId = 0;
        this.parentRow = null;
        this.joinList = null;

        this.backHandler = null;
        this.nextHandler = null;
        this.stepHandler = null;

        this.addForm = null;
        this.copyForm = null;
        this.updateForm = null;
        this.deleteForm = null;
        this.addFormString = null;
        this.copyFormString = null;
        this.updateFormString = null;
        this.deleteFormString = null;
        this.parentBackHandler = null;
        this.parentNextHandler = null;
        this.parentStepHandler = null;

        this.postSubmitHandler = null;

        // as form component
        this.name = null;
        this.fieldType = "DataTable";
        this.min = null;
        this.max = null;
        this.validator_messages = null;
        this.errorMessage = "";
        this.value = [];

        this.initialized = false;

        this.addEventListener(`grid-select-all-${this.instanceId}`, this.handleSelectAll);
        this.addEventListener(`grid-upload-image-${this.instanceId}`, this.handleUploadImage);
        this.addEventListener(`grid-viewer-${this.instanceId}`, this.handleViewer);
        this.addEventListener(`grid-add-${this.instanceId}`, this.handleAdd);
        this.addEventListener(`grid-copy-${this.instanceId}`, this.handleCopy);
        this.addEventListener(`grid-update-${this.instanceId}`, this.handleUpdate);
        this.addEventListener(`grid-delete-${this.instanceId}`, this.handleDelete);
        this.addEventListener(`grid-filter-${this.instanceId}`, this.handleFilter);
        this.addEventListener(`grid-apply-filter-${this.instanceId}`, this.handleApplyFilter);
        this.addEventListener(`grid-columns-${this.instanceId}`, this.handleColumns);
        this.addEventListener(`grid-columns-update-${this.instanceId}`, this.handleColumnsUpdate);
        this.addEventListener(`grid-bookmark-${this.instanceId}`, this.handleBookmark);
        this.addEventListener(`grid-refresh-${this.instanceId}`, this.handleRefresh);
        this.addEventListener(`grid-auto-refresh-${this.instanceId}`, this.handleAutoRefresh);
        this.addEventListener(`grid-apply-auto-refresh-${this.instanceId}`, this.handleApplyAutoRefresh);
        this.addEventListener(`grid-copy-to-clipboard-${this.instanceId}`, this.handleCopyClipboard);
        this.addEventListener(`grid-download-pdf-${this.instanceId}`, this.handleDownloadPDF);
        this.addEventListener(`grid-download-excel-${this.instanceId}`, this.handleDownloadExcel);
        this.addEventListener(`grid-download-csv-${this.instanceId}`, this.handleDownloadCsv);
        this.addEventListener(`grid-print-${this.instanceId}`, this.handlePrint);

        this.addEventListener(`grid-row-selected-${this.instanceId}`, this.handleRowSelected);
        this.addEventListener(`grid-row-opened-${this.instanceId}`, this.handleRowOpened);
        this.addEventListener(`grid-sort-column-${this.instanceId}`, this.handleSortColumn);
        this.addEventListener(`grid-drop-column-${this.instanceId}`, this.handleDropColumn);

        this.addEventListener(`tab-select-${this.instanceId}`, this.handleTabSelect);

        this.addEventListener(`grid-rows-per-page-change-${this.instanceId}`, this.handleRowsPerPageChange);
        this.addEventListener(`grid-page-change-${this.instanceId}`, this.handlePageChange);

        this.addEventListener(`grid-child-update-${this.instanceId}`, this.handleChildGridUpdate);

        this.addEventListener(`form-cancel-${this.instanceId}`, this.toggleCollapse);
        this.addEventListener(`form-submit-${this.instanceId}`, this.handleFormSubmit);
        this.addEventListener(`form-submit-post-post-${this.instanceId}`, this.handleFormClose);
        this.addEventListener(`form-submit-post-put-${this.instanceId}`, this.handleFormClose);
        this.addEventListener(`form-submit-post-delete-${this.instanceId}`, this.handleFormClose);
    }

    async connectedCallback() {
        super.connectedCallback();

        if(isEmpty(this.label)) this.label = this.title;

        if(!isEmpty(this.gridOptions)) {
            if("toolbar" in this.gridOptions)  this.toolbar = this.gridOptions.toolbar;
            if("footer" in this.gridOptions)  this.footbar = this.gridOptions.footer;
        }
        if(isNull(this.addButtonInit)) this.addButtonInit = this.addButton;
        if(isNull(this.copyButtonInit)) this.copyButtonInit =  this.copyButton;
        if(isNull(this.updateButtonInit)) this.updateButtonInit =  this.updateButton;
        if(isNull(this.deleteButtonInit)) this.deleteButtonInit =  this.deleteButton;

        this.addButton = false;
        this.copyButton = false;
        this.updateButton = false;
        this.deleteButton = false;
        this.viewerButton = false;

        this.totalRows = isArray(this.gridData) ? this.gridData.length : 0;

        if(this.program && !this.stateless) {
            try {
                await api.GET(`/getProgram/${this.program}/Grid/${this.tableLevel}`, null)
                    .then(data => {
                        if(Object.keys(data.data).length > 0) {
                            this.securityLevel.runLevel = data.data.RunLevel;
                            this.securityLevel.createLevel = data.data.CreateLevel;
                            this.securityLevel.updateLevel = data.data.UpdateLevel;
                            this.securityLevel.deleteLevel = data.data.DeleteLevel;

                            this.bookmarked = data.data.is_bookmarked;
                            if(this.bookmarked) this.bookmarkButton = false;
                            if(this.addButtonInit && store.get("user.Role.CreateLevel") >= this.securityLevel.createLevel) {
                                this.addButton = true;
                            }
                        } else {
                            try {
                                const params = {
                                    "Depth": this.tableLevel,
                                    "CompanyRowId": store.get("user.Company_Id"),
                                    "Locale": store.get("user.Settings.Locale")[0],
                                    "Timezone": store.get("user.Settings.Timezone")[0],
                                    "DbTableName": "Programs",
                                    "RowId": 0,
                                    "Schema": null,
                                    "Data": {
                                        "Program": this.program,
                                        "Name": this.title,
                                        "Type": "Grid",
                                        "Table": this.dbTable,
                                        "Override": true,
                                        "URL": "", // must be a script called program - dont create a url
                                        "RunLevel": this.securityLevel.runLevel,
                                        "CreateLevel": this.securityLevel.createLevel,
                                        "UpdateLevel": this.securityLevel.updateLevel,
                                        "DeleteLevel": this.securityLevel.deleteLevel
                                    }
                                };
                                if(!this.initialized) {
                                    // guard against tab init/select race condition
                                    this.initialized = true;
                                    api.POST("/createTable", params, "json");
                                }
                                if(this.addButtonInit && store.get("user.Role.CreateLevel") >= this.securityLevel.createLevel) {
                                    this.addButton = true;
                                }
                            } catch (err) {
                                console.log("datatable.connectedCallback1 error:", err);
                                const message = `datatable.connectedCallback1 ${err.status}  ${err.detail} : datatable.connectedCallback.createProgram ${this.dbTable}`;
                                const toaster = document.querySelector("[data-toaster]");
                                toaster.show(message,"error");
                            }
                        }
                    });
            } catch (err) {
                console.log("datatable.connectedCallback2 error:", err);
                const message = `datatable.connectedCallback2 ${err.status}  ${err.detail} : datatable.connectedCallback.getProgram ${this.dbTable}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        }

        this.getGridSchema();
        if(this.autoRefresh) this.setAutoRefreshTimer();
    }

    disconnectedCallback() {
        super.disconnectedCallback();

        this.clearAutoRefreshTimer();
    }

    async getGridSchema() {
        if(this.getGridSchemaEvent) {
            const data = await new Promise((resolve, reject) => {
                this.dispatchEvent(new CustomEvent(`grid-get-schema-${this.ownerId}`, {
                    detail: { resolve, reject },
                    bubbles: true,
                    composed: true
                }));
            });
            this.getGridState(data.grid_fields, data.grid_tables);
        } else if(this.getGridSchemaHandler) {
            const data = await this.getGridSchemaHandler();
            this.getGridState(data.grid_fields, data.grid_tables);
        } else {
            let url = `/gridSchema/${this.dbTable}`;
            if(!isEmpty(this.getGridSchemaURL))  url = this.getGridSchemaURL;
            try {
                await api.GET(url, null)
                    .then(data => {
                        data.grid_fields.forEach( field => {
                            field.options = {
                                "sort": false,
                                "sortDirection": "none",
                                "display": field.visible,
                                "modifiable": field.modifiable
                            };
                        });
                        this.getGridState(data.grid_fields, data.grid_tables)
                    });
            } catch(err) {
                console.log("datatable.getGridSchema error:", err);
                const message = `datatable.getGridSchema ${err.status}  ${err.detail} : datatable.getGridSchema ${this.dbTable}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        }
    }

    saveGridState() {
        if(this.stateless) return false;

        try {
            const params = {
                "CompanyRowId": store.get("user.Company_Id"),
                "Program": this.program,
                "ProgramType": "Grid",
                "Param1": null,
                "Param2": null,
                "Param3": null,
                "Param4": null,
                "Param5": null,
                "Level": this.tableLevel,
                "CurrentPage": this.currentPage,
                "PageSize": this.rowsPerPage,
                "AutoRefresh": this.autoRefresh,
                "RefreshInterval": this.refreshInterval,
                "State": {
                    "grid_fields": this.gridColumns,
                    "grid_tables": this.gridTables,
                    "criteria": this.criteria,
                    "criteria_type": this.criteriaType,
                    //"multiple_select": this.multiSelect,
                    "all_rows_selected": this.allRowsSelected,
                    "selected_rows": this.selectedRows,
                    "open_rows": this.openRows,
                    "tab_select": this.tabSelect,
                    "buttons": {
                        // add,copy,update,delete buttons not saved as these
                        // are controlled by security and form mode
                        "filter": this.filterButton,
                        "columns": this.columnButton,
                        "bookmark": this.bookmarkButton,
                        "refresh": this.refreshButton,
                        "auto_refresh": this.autoRefreshButton,
                        "download": this.downloadButton,
                        "print": this.printButton
                    }
                }
            };
            api.POST("/updateProgramState", params, "json");
        } catch(err) {
            console.log("datatable.saveGridState error:", err);
            const message = `datatable.saveGridState ${err.status}  ${err.detail} : datatable.saveGridState ${this.dbTable}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    async getGridState(columns, tables) {
        if(this.stateless) {
            this.gridColumns = columns;
            this.gridTables = tables;

            if(!this.inputDataGrid) this.getGridData(null, null, true);

            return false;
        }
        try {
            const params = {
                "CompanyRowId": store.get("user.Company_Id"),
                "Program": this.program,
                "ProgramType": "Grid",
                "Param1": null,
                "Param2": null,
                "Param3": null,
                "Param4": null,
                "Param5": null
            };
            await api.POST("/getProgramState", params, "json").then(data => {
                if(!isEmpty(data.State) && Object.keys(data.State).length > 0) {
                    this.tableLevel = data.Level;
                    this.currentPage = data.CurrentPage;
                    this.rowsPerPage = data.PageSize;
                    this.autoRefresh = data.AutoRefresh;
                    this.refreshInterval = data.RefreshInterval;
                    //this.multiSelect = data.State.multiple_select;
                    this.allRowsSelected = data.State.all_rows_selected;
                    if(!this.inputDataSelect) {
                        this.selectedRows = data.State.selected_rows;
                        this.criteria = data.State.criteria;
                        this.criteriaType = data.State.criteria_type;
                    }
                    this.openRows = data.State.open_rows;
                    this.tabSelect = data.State.tab_select;
                    // add,copy,update,delete buttons not saved as these
                    // are controlled by security and form mode
                    this.filterButton = data.State.buttons.filter;
                    this.columnButton = data.State.buttons.columns;
                    this.bookmarkButton = data.State.buttons.bookmark;
                    this.refreshButton = data.State.buttons.refresh;
                    this.autoRefreshButton = data.State.buttons.auto_refresh;
                    this.downloadButton = data.State.buttons.download;
                    this.printButton = data.State.buttons.print;

                    // form component
                    if(this.name && this.ownerId) {
                        this.setFormData();
                    }

                    if(this.bookmarked) this.bookmarkButton = false;

                    if(!isEmpty(this.selectedRows)) {
                        if(this.copyButtonInit && store.get("user.Role.CreateLevel") >= this.securityLevel.createLevel) this.copyButton = true;
                        if(this.updateButtonInit && store.get("user.Role.UpdateLevel") >= this.securityLevel.updateLevel) this.updateButton = true;
                        if(this.deleteButtonInit && store.get("user.Role.DeleteLevel") >= this.securityLevel.deleteLevel) this.deleteButton = true;
                    }
                    // column definition might have change after save
                    let panel_fields = [];
                    data.State.grid_fields.forEach(ele => {
                        const col = columns.find(obj => {
                                    return obj.name === ele.name;
                        });
                        if(!isEmpty(col)) {
                            panel_fields.push(ele);
                        }
                    });
                    if(isEmpty(panel_fields)) {
                        panel_fields = columns;
                    } else {
                        // apply columns not in saved columns
                        columns.forEach(ele => {
                            const col = panel_fields.find(obj => {
                                    return obj.name === ele.name;
                            });
                            if(isEmpty(col)) {
                                panel_fields.push(ele);
                            }
                        });
                    }
                    this.gridColumns = panel_fields;
                    this.gridTables = data.State.grid_tables;
                } else  {
                    this.gridColumns = columns;
                    this.gridTables = tables;
                }
                if(!this.inputDataGrid) this.getGridData(null, null, true);

                if(!isEmpty(this.selectedRows)) {
                    if("viewer" in this.gridTables[0] && this.gridTables[0].viewer) {
                        this.viewerButton = true;
                    }
                }
            });
        } catch(err) {
            console.log("datatable.getGridState error:", err);
            const message = `datatable.getGridState ${err.status}  ${err.detail} : datatable.getGridState ${this.dbTable}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    // setData from parent components ie: ui-stepper
    setData(data) {
        this.localData = true;

        this.gridData = data;
        this.totalRows = isArray(data) ? data.length : 0;
    }

    async getGridData(messageType="", message="", initialLoad=false) {
        const page = Math.max(0, this.currentPage - 1);

        let crit = structuredClone(this.criteria);  // deep copy
        let crit_type = structuredClone(this.criteriaType);  // deep copy

        if(!isEmpty(this.getGridDataFilter)) {
            crit_type = 0;
            crit = [];
            this.getGridDataFilter.forEach(ele => {
                let val = null;
                if(isNil(ele.value)) {
                    if(this.owner) {
                        const data = this.owner.getData();
                        val = get(data, ele.field, null);
                    }
                } else {
                    val = ele.value;
                }
                if(val) {
                    const ops = criteriaOps2Int(ele.op);
                    crit.push({"field": ele.field, "op": ops, "value": val })
                }
            });
        }

        if(this.getGridDataEvent) {
            const result = await new Promise((resolve, reject) => {
                this.dispatchEvent(new CustomEvent(`grid-get-data-${this.ownerId}`, {
                    detail: {
                        gridColumns: this.gridColumns,
                        criteria: structuredClone(crit),
                        criteriaType: structuredClone(crit_type),
                        page: page,
                        pageSize: this.rowsPerPage,
                        selectedRows: initialLoad ? structuredClone(this.selectedRows) : [],
                        parentTable: this.parentTable,
                        parentField: this.parentField,
                        parentRowId: this.parentRowId,
                        parentRow: this.parentRow,
                        resolve, reject
                    },
                    bubbles: true,
                    composed: true,
                }));
            });
            this.gridData = result.data;
            this.totalRows = result.recordsTotal;

            if(initialLoad && !isEmpty(this.selectedRows)) {
                this.selectedRows = result.selectedRows;
                if(isEmpty(this.selectedRows)) {
                    if(this.copyButtonInit && store.get("user.Role.CreateLevel") >= this.securityLevel.createLevel) this.copyButton = false;
                    if(this.updateButtonInit && store.get("user.Role.UpdateLevel") >= this.securityLevel.updateLevel) this.updateButton = false;
                    if(this.deleteButtonInit && store.get("user.Role.DeleteLevel") >= this.securityLevel.deleteLevel) this.deleteButton = false;

                    this.viewerButton = false;
                }
                // form component
                if(this.name && this.ownerId) {
                    this.setFormData();
                }
            }

            if(message && messageType) {
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message, messageType);
            }
            return;
        }

        if(this.getGridDataHandler) {
            const result = await this.getGridDataHandler(
                                                this.gridColumns,
                                                crit,
                                                crit_type,
                                                page,
                                                this.rowsPerPage,
                                                initialLoad ? this.selectedRows : [],
                                                this.parentTable,
                                                this.parentField,
                                                this.parentRowId
                                                );
            this.gridData = result.data;
            this.totalRows = result.recordsTotal;

            if(initialLoad && !isEmpty(this.selectedRows)) {
                this.selectedRows = result.selectedRows;
                if(isEmpty(this.selectedRows)) {
                    if(this.copyButtonInit && store.get("user.Role.CreateLevel") >= this.securityLevel.createLevel) this.copyButton = false;
                    if(this.updateButtonInit && store.get("user.Role.UpdateLevel") >= this.securityLevel.updateLevel) this.updateButton = false;
                    if(this.deleteButtonInit && store.get("user.Role.DeleteLevel") >= this.securityLevel.deleteLevel) this.deleteButton = false;

                    this.viewerButton = false;
                }
                // form component
                if(this.name && this.ownerId) {
                    this.setFormData();
                }
            }

            if(message && messageType) {
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message, messageType);
            }
            return;
        }

        if(this.localData && !isEmpty(this.parentRow)) {
           this.gridData = get(this.parentRow, this.parentField, []);
           this.totalRows = this.gridData.length;

            if(message && messageType) {
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message, messageType);
            }
            return;
        }

        if(!isEmpty(this.getGridDataURL)) {
            try {
                const offset = page * (this.rowsPerPage > 0 ? this.rowsPerPage : 0);
                let url = `${this.getGridDataURL}/${this.rowsPerPage}/${offset}`;
                await api.GET(url, null).then(result => {
                    this.gridData = result.data;
                    this.totalRows = result.recordsTotal;

                    if(initialLoad && !isEmpty(this.selectedRows)) {
                        this.selectedRows = result.selectedRows;
                        if(isEmpty(this.selectedRows)) {
                            if(this.copyButtonInit && store.get("user.Role.CreateLevel") >= this.securityLevel.createLevel) this.copyButton = false;
                            if(this.updateButtonInit && store.get("user.Role.UpdateLevel") >= this.securityLevel.updateLevel) this.updateButton = false;
                            if(this.deleteButtonInit && store.get("user.Role.DeleteLevel") >= this.securityLevel.deleteLevel) this.deleteButton = false;

                            this.viewerButton = false;
                        }
                        // form component
                        if(this.name && this.ownerId) {
                            this.setFormData();
                        }
                    }

                    if(message && messageType) {
                        const toaster = document.querySelector("[data-toaster]");
                        toaster.show(message, messageType);
                    }
                });
            } catch(err) {
                console.log("datatable.getGridData1 error:", err);
                const message = `datatable.getGridData1 ${err.status}  ${err.detail} : datatable.getGridData ${this.dbTable}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
            return;
        }

        try {
            const params = {
                    "Depth": this.tableLevel,
                    "CompanyRowId": store.get("user.Company_Id"),
                    "Locale": store.get("user.Settings.Locale")[0],
                    "Timezone": store.get("user.Settings.Timezone")[0],
                    "FieldList": [],
                    "DbTableName": this.dbTable,
                    "Criteria": crit,
                    "CriteriaType": crit_type, // ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3
                    "Columns": this.gridColumns,
                    "Offset": page * (this.rowsPerPage > 0 ? this.rowsPerPage : 0),
                    "PageSize": this.rowsPerPage,
                    "ChoicesAsTuple": false,
                    "ChoicesKey": true,
                    "TextAsString": true,
                    "Draw": 1,
                    "SelectedRows": initialLoad ? this.selectedRows : [],
                    "ParentTable": this.parentTable,
                    "ParentField": this.parentField,
                    "ParentRowId": this.parentRowId
            };
            let url = "/list";
            if(this.parentTable) url = "/listChild";
            if(!isEmpty(this.postGridDataURL))  url = this.postGridDataURL;

            await api.POST(url, params, "json").then(result => {
                this.gridData = result.data;
                this.totalRows = result.recordsTotal;

                if(initialLoad && !isEmpty(this.selectedRows)) {
                    this.selectedRows = result.selectedRows;
                    if(isEmpty(this.selectedRows)) {
                        if(this.copyButtonInit && store.get("user.Role.CreateLevel") >= this.securityLevel.createLevel) this.copyButton = false;
                        if(this.updateButtonInit && store.get("user.Role.UpdateLevel") >= this.securityLevel.updateLevel) this.updateButton = false;
                        if(this.deleteButtonInit && store.get("user.Role.DeleteLevel") >= this.securityLevel.deleteLevel) this.deleteButton = false;

                        this.viewerButton = false;
                    }
                    // form component
                    if(this.name && this.ownerId) {
                        this.setFormData();
                    }
                }

                if(message && messageType) {
                    const toaster = document.querySelector("[data-toaster]");
                    toaster.show(message, messageType);
                }
            });
        } catch(err) {
                console.log("datatable.getGridData2 error:", err);
                const message = `datatable.getGridData2 ${err.status}  ${err.detail} : datatable.getGridData ${this.dbTable}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
        }
    }

    toggleCollapse() {
        if (this.collapse.classList.contains("collapse-open")) {
            this.collapse.classList.add("collapse-close");
            this.collapse.classList.remove("collapse-open");
            this.crudMode = null;
            return null;
        }
        this.collapse.classList.add("collapse-open");
        this.collapse.classList.remove("collapse-close");

        return this.collapse.querySelector('ui-container');
    }

    handleSelectAll(event) {
        // bubbled up event from datatable-header
        this.allRowsSelected = event.detail.value;
        if(this.allRowsSelected) this.selectedRows = [];
        // form component
        if(this.name && this.ownerId) {
            this.setFormData();
        }

        this.saveGridState();
    }

    handleUploadImage(event) {
        // bubbled up event from datatable-header
        const content = this.toggleCollapse();
        if(content === null) return false;

        const table = this.gridTables[0];

        const component = document.createElement("ui-uploadimageform");
        component.ownerId = this.instanceId;
        component.owner = this;
        component.dbTable = table.table;
        component.formButtons = true;
        component.parentTable = this.parentTable;
        component.parentField = this.parentField;
        component.parentRowId = this.parentRowId;
        component.parentRow = this.parentRow;
        component.joinList = this.joinList;
        component.program = `${this.program}.${table.table}`;
        component.securityLevel = this.securityLevel;
        component.ownerCancelHandler = true;

        let formData = null;
        if(this.selectedRows[0]) {
            formData = structuredClone(this.gridData.find(item => item.Id === this.selectedRows[0]));  // deep copy
            component.mode = "Update";
            component.submitText = "Update";
            component.rowId = this.selectedRows[0];
        } else {
            component.mode = "Create";
            component.submitText = "Create";
        }

        if(this.localData) {
            component.ownerSubmitHandler = true;
            if(formData) {
                component.formType = "LocalUpdateImage";
                component.rowId = 0;  // force to use component.formData
                component.formData = formData;
            }
            else component.formType = "LocalAddImage";
        } else component.ownerSubmitPostPostHandler = true;

        content.addElement(component);
    }

    handleViewer(event) {
        if(isEmpty(this.selectedRows)) return false;

        const row = this.gridData.find(item => item.Id === this.selectedRows[0]);

        let uri = null;
        switch(this.gridTables[0].viewer.type.toLowerCase()) {
            case "imageviewer":
                let title = this.gridTables[0].viewer.title;
                let file = get(row, this.gridTables[0].viewer.file_field);
                uri = "/imageviewer/" + encodeURIComponent(title) + "/" + encodeURIComponent(file);
                break;
        }
        if(uri) {
            navigateTo(uri);
        }
    }

    handleAdd(event) {
        // bubbled up event from datatable-header
        const content = this.toggleCollapse();
        if(content === null) return false;

        this.crudMode = "Create";
        const table = this.gridTables[0];

        if(this.addFormString) {
            const myFunction = window[this.addFormString];
            if (isFunction(myFunction)) {
                return myFunction(content, this);
            }
        }
        if(this.addForm) {
            return this.addForm(content, this);
        }
        const component = document.createElement("ui-form");
        component.ownerId = this.instanceId;
        component.owner = this;
        component.title = `New ${table.desc || table.label}`;
        component.dbTable = table.table;
        component.mode = "Create";
        component.formButtons = true;
        component.submitText = "Create";
        component.parentTable = this.parentTable;
        component.parentField = this.parentField;
        component.parentRowId = this.parentRowId;
        component.parentRow = this.parentRow;
        component.joinList = this.joinList;
        component.program = `${this.program}.${table.table}`;
        component.securityLevel = this.securityLevel;
        component.ownerCancelHandler = true;
        if(this.localData) {
            component.ownerSubmitHandler = true;
            component.formType = "LocalAdd";
        } else component.ownerSubmitPostPostHandler = true;

        content.addElement(component);
    }

    handleLocalAdd(event) {
        let last_id = 0;
        this.gridData.forEach(row => {
            last_id = Math.max(last_id, row.Id);
        });

        const record = {};
        Object.entries(event.detail.value).forEach(([key, value]) => {
            record[key] = value;
        });
        record["Id"] = last_id + 1;
        record["__mode"] = "Add";

        this.gridData.push(record);
        this.totalRows = this.gridData.length;
        this.table.gridData = this.gridData;
        if(this.ownerId && this.parentField && !isEmpty(this.parentRow)) {
            this.dispatchEvent(new CustomEvent(`grid-child-update-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    field: this.parentField,
                    rowId: this.parentRowId,
                    value: this.gridData
                }
            }));
        }
        this.table.requestUpdate();  // force render
    }

    handleCopy(event) {
        // bubbled up event from datatable-header
        const content = this.toggleCollapse();
        if(content === null) return false;

        this.crudMode = "Copy";
        // formData can be stale

        const formData = structuredClone(this.gridData.find(item => item.Id === this.selectedRows[0])); // deepcopy
        const table = this.gridTables[0];

        // bespoke copyForm should handle fresh data - formData can be stale
        if(this.copyFormString) {
            const myFunction = window[this.copyFormString];
            if (isFunction(myFunction)) {
                return myFunction(content, formData, this);
            }
        }
        if(this.copyForm) {
            return this.copyForm(content, formData, this);
        }

        const component = document.createElement("ui-form");
        component.ownerId = this.instanceId;
        component.owner = this;
        component.title = `Copy ${table.desc || table.label}`;
        component.dbTable = table.table;
        component.rowId = this.selectedRows[0];  // always get fresh data
        component.mode = "Copy";
        component.formButtons = true;
        component.submitText = "Copy";
        component.parentTable = this.parentTable;
        component.parentField = this.parentField;
        component.parentRowId = this.parentRowId;
        component.parentRow = this.parentRow;
        component.joinList = this.joinList;
        component.program = `${this.program}.${table.table}`;
        component.securityLevel = this.securityLevel;

        component.ownerCancelHandler = true;
        if(this.localData) {
            component.ownerSubmitHandler = true;
            component.formType = "LocalCopy";
            component.rowId = 0;  // force to use component.formData
            component.formData = formData;
        } else component.ownerSubmitPostPostHandler = true;
        content.addElement(component);
    }

    handleLocalCopy(event) {
        let last_id = 0;
        this.gridData.forEach(row => {
            last_id = Math.max(last_id, row.Id);
        });

        const record = {};
        Object.entries(event.detail.value).forEach(([key, value]) => {
            record[key] = value;
        });
        record["Id"] = last_id + 1;
        record["__mode"] = "Add";

        this.gridData.push(record);
        this.totalRows = this.gridData.length;
        this.table.gridData = this.gridData;
        if(this.ownerId && this.parentField && !isEmpty(this.parentRow)) {
            this.dispatchEvent(new CustomEvent(`grid-child-update-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    field: this.parentField,
                    rowId: this.parentRowId,
                    value: this.gridData
                }
            }));
        }

        this.table.requestUpdate();  // force render
    }

    handleUpdate(event) {
        // bubbled up event from datatable-header
        const content = this.toggleCollapse();
        if(content === null) return false;

        this.crudMode = "Update";
        // formData can be stale
        const formData = structuredClone(this.gridData.find(item => item.Id === this.selectedRows[0]));  // deep copy
        const table = this.gridTables[0];

        // bespoke updateForm should handle fresh data - formData can be stale
        if(this.updateFormString) {
            const myFunction = window[this.updateFormString];
            if (isFunction(myFunction)) {
                return myFunction(content, formData, this);
            }
        }
        if(this.updateForm) {
            return this.updateForm(content, formData, this);
        }

        const component = document.createElement("ui-form");
        component.ownerId = this.instanceId;
        component.owner = this;
        component.title = `Update ${table.desc || table.label}`;
        component.dbTable = table.table;
        component.rowId = this.selectedRows[0];  // always get fresh data
        component.mode = "Update";
        component.formButtons = true;
        component.submitText = "Update";
        component.parentTable = this.parentTable;
        component.parentField = this.parentField;
        component.parentRowId = this.parentRowId;
        component.parentRow = this.parentRow;
        component.joinList = this.joinList;
        component.program = `${this.program}.${table.table}`;
        component.securityLevel = this.securityLevel;
        component.ownerCancelHandler = true;
        if(this.localData) {
            component.ownerSubmitHandler = true;
            component.formType = "LocalUpdate";
            component.rowId = 0;  // force to use component.formData
            component.formData = formData;
        } else component.ownerSubmitPostPutHandler = true;
        content.addElement(component);
    }

    handleLocalUpdate(event) {
        const record = this.gridData.find(item => item.Id === event.detail.rowId);

        Object.entries(event.detail.value).forEach(([key, value]) => {
            record[key] = value;
        });

        this.table.gridData = this.gridData;
        if(this.ownerId && this.parentField && !isEmpty(this.parentRow)) {
            this.dispatchEvent(new CustomEvent(`grid-child-update-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    field: this.parentField,
                    rowId: this.parentRowId,
                    value: this.gridData
                }
            }));
        }

        this.table.requestUpdate();  // force render
    }

    handleDelete(event) {
        // bubbled up event from datatable-header
        const content = this.toggleCollapse();
        if(content === null) return false;

        this.crudMode = "Delete";
        // formData can be stale
        const formData = structuredClone(this.gridData.find(item => item.Id === this.selectedRows[0])); // deep copy
        const table = this.gridTables[0];

        // bespoke deleteForm should handle fresh data - formData can be stale
        if(this.deleteFormString) {
            const myFunction = window[this.deleteFormString];
            if (isFunction(myFunction)) {
                return myFunction(content, formData, this);
            }
        }
        if(this.deleteForm) {
            return this.deleteForm(content, formData, this);
        }

        const component = document.createElement("ui-form");
        component.ownerId = this.instanceId;
        component.owner = this;
        component.title = `Delete ${table.desc || table.label}`;
        component.dbTable = table.table;
        component.rowId = this.selectedRows[0]; // always get fresh data
        component.mode = "Delete";
        component.formButtons = true;
        component.submitText = "Delete";
        component.parentTable = this.parentTable;
        component.parentField = this.parentField;
        component.parentRowId = this.parentRowId;
        component.parentRow = this.parentRow;
        component.joinList = this.joinList;
        component.program = `${this.program}.${table.table}`;
        component.securityLevel = this.securityLevel;

        component.ownerCancelHandler = true;
        if(this.localData) {
            component.ownerSubmitHandler = true;
            component.formType = "LocalDelete";
            component.rowId = 0;  // force to use component.formData
            component.formData = formData;
        } else component.ownerSubmitPostDeleteHandler = true;

        content.addElement(component);
    }

    handleLocalDelete(event) {
        let index = this.selectedRows.indexOf(event.detail.rowId);
        if (index > -1) {
            this.selectedRows.splice(index, 1);
            if(this.selectedRows.length === 0) {
                this.copyButton = false;
                this.updateButton = false;
                this.deleteButton = false;

                this.viewerButton = false;
            }
            this.saveGridState();
            this.table.selectedRows = this.selectedRows;
            // form component
            if(this.name && this.ownerId) {
                this.setFormData();
            }
        }

        index = this.gridData.findIndex(item => item.Id === event.detail.rowId);
        if(index > -1) {
            this.gridData.splice(index,1);
        }

        this.totalRows = this.gridData.length;
        this.table.gridData = this.gridData;
        if(this.ownerId && this.parentField && !isEmpty(this.parentRow)) {
            this.dispatchEvent(new CustomEvent(`grid-child-update-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    field: this.parentField,
                    rowId: this.parentRowId,
                    value: this.gridData
                }
            }));
        }

        this.table.requestUpdate();  // force render
    }

    handleFormSubmit(event) {
        if(event.detail.type === "BookmarkThisPage") this.handleBookmarkUpdate(event);
        else if(event.detail.type === "LocalAdd") this.handleLocalAdd(event);
        else if(event.detail.type === "LocalCopy") this.handleLocalCopy(event);
        else if(event.detail.type === "LocalUpdate") this.handleLocalUpdate(event);
        else if(event.detail.type === "LocalDelete") this.handleLocalDelete(event);
        else {
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(`datatable.handleFormSubmit not yet Implemented ${event.detail.type}`,
                        "error");
        }

        this.toggleCollapse();
    }

    handleChildGridUpdate(event) {
        const record = this.gridData.find(item => item.Id === event.detail.rowId);
        if(record) {
            set(record, event.detail.field, event.detail.value);

            if(this.ownerId && this.parentField && !isEmpty(this.parentRow)) {
                this.dispatchEvent(new CustomEvent(`grid-child-update-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: {
                        field: this.parentField,
                        rowId: this.parentRowId,
                        value: this.gridData
                    }
                }));
            }
        }
    }

    handleFormClose(event) {
        this.toggleCollapse();

        if(event.detail.mode === "Delete") {
            // remove from selectedRows
            const row_id = parseInt(event.detail.value.RecordRowId);
            const indexToItem = this.selectedRows.indexOf(row_id);
            if (indexToItem !== -1) {
                this.selectedRows.splice(indexToItem, 1);
                if(this.selectedRows.length === 0) {
                    this.copyButton = false;
                    this.updateButton = false;
                    this.deleteButton = false;

                    this.viewerButton = false;
                }
                this.saveGridState();
                this.table.selectedRows = this.selectedRows;
                // form component
                if(this.name && this.ownerId) {
                    this.setFormData();
                }
            }
        }

        if(this.postSubmitHandler) {
            const myFunction = window[this.postSubmitHandler];
            if (isFunction(myFunction)) {
                myFunction(event);
            }
        }

        this.getGridData();
        this.table.gridData = this.gridData;
    }

    handleFilter(event) {
        // bubbled up event from datatable-header
        const content = this.toggleCollapse();
        if(content === null) return false;

        const component = document.createElement("datatable-filter");
        component.datatableId = this.instanceId;
        component.gridColumns = this.gridColumns;
        component.criteria = this.criteria;
        component.criteriaType = this.criteriaType;

        content.addElement(component);
    }

    handleApplyFilter(event) {
        // bubbled up event from datatable-filter
        this.criteria = event.detail.criteria;
        this.criteriaType = event.detail.type;

        this.collapse.classList.add("collapse-close");
        this.collapse.classList.remove("collapse-open");

        this.header.totalCrits = this.criteria.length;

        this.saveGridState();

        this.getGridData();
        this.table.gridData = this.gridData;
    }

    handleColumns(event) {
        // bubbled up event from datatable-header
        if(this.gridColumns) {
            this.columns.gridColumns = this.gridColumns;
            this.columns.show();
        }
    }

    handleColumnsUpdate(event) {
        // bubbled up event from datatable-columns

        let grid_fields = [];
        // displayable fields first
        event.detail.value.forEach( field => {
            if(field.options.display) {
                grid_fields.push(field);
            }
        });
        // non displayable fields next
        event.detail.value.forEach( field => {
            if(!field.options.display) {
                grid_fields.push(field);
            }
        });

        this.gridColumns = grid_fields;

        this.saveGridState();

        this.table.gridColumns = this.gridColumns;
        if(event.detail.dirty) {
            this.getGridData();
        }
    }

    handleBookmark(event) {
        // bubbled up event from datatable-header
        const content = this.toggleCollapse();
        if(content === null) return false;

        const component = document.createElement("ui-form");
        component.ownerId = this.instanceId;
        component.title = "Bookmark this Page";
        component.dbTable = "Bookmarks";
        component.formFields = ["Desc", "HomePage", "HomePageSequence"];
        component.mode = "Create"
        component.formButtons = true;
        component.submitText = "Bookmark";
        component.formType = "BookmarkThisPage";
        component.ownerCancelHandler = true;
        component.ownerSubmitHandler = true;
        content.addElement(component);
    }

    async handleBookmarkUpdate(event) {
        const data = new URLSearchParams();
        data.append('title', event.detail.value.Desc);
        data.append('home_page', event.detail.value.HomePage);
        data.append('home_page_seq', event.detail.value.HomePageSequence === "" ? 0 : event.detail.value.HomePageSequence);
        data.append('page_type', "Grid");
        data.append('program', this.program);
        data.append('company_id', store.get("user.Company_Id"));

        try {
            await api.POST("/addToBookmarks", data)
                .then(data => {
                    menu.refreshBookmarks(data);
                });
        } catch (err) {
            console.log("datatable.handleBookmarkUpdate error:", err);
            const message = `datatable.handleBookmarkUpdate ${err.status}  ${err.detail} : datatable.handleBookmarkUpdate ${this.dbTable}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    handleRefresh(event) {
        // bubbled up event from datatable-header
        if(this.gridColumns) {
            this.getGridData("info", "Table Refreshed");
            this.table.gridData = this.gridData;
        }
    }

    handleAutoRefresh(event) {
        // bubbled up event from datatable-header
        const content = this.toggleCollapse();
        if(content === null) return false;

        const component = document.createElement("datatable-auto-refresh");
        component.datatableId = this.instanceId;
        component.interval = this.refreshInterval;
        component.enable = this.autoRefresh;

        content.addElement(component);
    }

    handleApplyAutoRefresh(event) {
        // bubbled up event from datatable-auto-refresh

        this.refreshInterval = parseInt(event.detail.interval);
        this.autoRefresh = event.detail.enable;

        this.collapse.classList.add("collapse-close");
        this.collapse.classList.remove("collapse-open");

        this.header.totalSecs = this.autoRefresh ? this.refreshInterval : 0;

        this.saveGridState();

        if(this.autoRefresh) this.setAutoRefreshTimer();
        else this.clearAutoRefreshTimer();
    }

    setAutoRefreshTimer() {
        if(this.timerId) {
            this.clearAutoRefreshTimer();
        }
        // use arrow function to maintain 'this' context
        this.timerId = setInterval(() => { this.getGridData(); },
                                    this.refreshInterval * 1000);
    }

    clearAutoRefreshTimer() {
        if(this.timerId) {
            clearInterval(this.timerId);
            this.timerId = null;
        }
    }

    async handleCopyClipboard(event) {
        // bubbled up event from datatable-header
        let textTable = `${this.title}\n\n`;

        const origTable = this.table.shadowRoot.querySelector('table');
        const table = origTable.cloneNode(true); // deep copy
        this.convertBoolIconToText(table);

        // Calculate the maximum width for each column
        const columnWidths = [];
        Array.from(table.rows).forEach(row =>{
            Array.from(row.cells).forEach((cell, index) => {
                columnWidths[index] = Math.max(columnWidths[index] || 0,
                                               cell.innerText.trim().length);
            });
        });
        for(let i = 0; i < table.rows.length; i++) {
            const row = table.rows[i];
            for(let j = 0; j < row.cells.length; j++) {
                const cell = row.cells[j];
                // Calculate the spacing based on the maximum width for the column
                const spacing = " ".repeat(columnWidths[j] - cell.innerText.trim().length + 1);
                textTable += cell.innerText.trim() + spacing;
            }
            textTable += "\n";
        }
        try {
            await navigator.clipboard.writeText(textTable);
            const toaster = document.querySelector("[data-toaster]");
            toaster.show("Copied to Clipboard", "info");
        } catch (err) {
            console.log("datatable.handleCopyClipboard error:", err);
            const message = `datatable.handleCopyClipboard ${err.status}  ${err.detail} : datatable.handleCopyClipboard ${this.dbTable}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    handleDownloadPDF(event) {
        // bubbled up event from datatable-header
        const origTable = this.table.shadowRoot.querySelector('table');
        const table = origTable.cloneNode(true); // deep copy
        this.convertBoolIconToText(table);

        // TODO: fit all table columns into one pdf document
        const opt = {
            filename: `${this.title.replace(/ /g, "_")}.pdf`,
            jsPDF: { orientation: 'landscape' }
        };
        // TODO: fix TypeError: this.createRenderRoot is not a function
        html2pdf(table, opt);
    }

    handleDownloadExcel(event) {
        // bubbled up event from datatable-header
        const origTable = this.table.shadowRoot.querySelector('table');
        const table = origTable.cloneNode(true); // deep copy
        this.convertBoolIconToText(table);

        // Create a new Blob object with the Excel content
        const blob = new Blob(
            [`
                <html xmlns:o="urn:schemas-microsoft-com:office:office" xmlns:x="urn:schemas-microsoft-com:office:excel" xmlns="http://www.w3.org/TR/REC-html40">
                    <head>
                        <!--[if gte mso 9]><xml><x:ExcelWorkbook><x:ExcelWorksheets><x:ExcelWorksheet><x:Name>Sheet1</x:Name><x:WorksheetOptions><x:DisplayGridlines/></x:WorksheetOptions></x:ExcelWorksheet></x:ExcelWorksheets></x:ExcelWorkbook></xml><![endif]-->
                    </head>
                    <body>
                        ${table.outerHTML}
                    </body>
                </html>
            `],
            { type: 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet' }
        );
        // Create a download link
        const link = document.createElement('a');
        link.href = URL.createObjectURL(blob);
        // Set the download attribute with the desired file name
        link.download = `${this.title.replace(/ /g, "_")}.xlsx`;
        // Append the link to the document and trigger a click to start the download
        document.body.appendChild(link);
        link.click();
        // Remove the link from the document after the download
        document.body.removeChild(link);
    }

    handleDownloadCsv(event) {
        // bubbled up event from datatable-header
        const origTable = this.table.shadowRoot.querySelector('table');
        const table = origTable.cloneNode(true); // deep copy
        this.convertBoolIconToText(table);

        let csvContent = "data:text/csv;charset=utf-8,";
        for(let i = 0; i < table.rows.length; i++) {
            const row = table.rows[i];
            const rowData = Array.from(row.cells).map(cell => cell.innerText.trim());
            const csvRow = rowData.join(',');

            csvContent += csvRow + '\n';
        }

        const encodedUri = encodeURI(csvContent);
        const link = document.createElement("a");
        link.setAttribute("href", encodedUri);
        link.setAttribute("download", `${this.title.replace(/ /g, "_")}.csv`);
        document.body.appendChild(link);
        link.click();
        document.body.removeChild(link);
    }

    handlePrint(event) {
        // bubbled up event from datatable-header
        const printWindow = window.open('', '_blank');

        const origTable = this.table.shadowRoot.querySelector('table');
        const table = origTable.cloneNode(true); // deep copy
        this.convertBoolIconToText(table);

        const printTableContent = `
            <!DOCTYPE html>
            <html lang="en">
                <head>
                    <meta charset="UTF-8">
                    <meta name="viewport" content="width=device-width, initial-scale=1.0">
                    <title>${this.title}</title>
                    <style>
                        ${TWStyles}
                    </style>
                </head>
                <body>
                    <div class="block w-full overflow-auto">
                        ${table.outerHTML}
                    </div>
                    <script>
                        window.onload = function() {
                            window.print();
                            window.onafterprint = function() {
                                window.close();
                            };
                        };
                    </script>
                </body>
            </html>
        `;
        printWindow.document.write(printTableContent);
        printWindow.document.close();
    }

    convertBoolIconToText(table) {
        const iconCells = table.querySelectorAll('icon-check, icon-x');
        iconCells.forEach(cell => {
            const text = cell.tagName.toLowerCase() === "icon-check" ? "yes" : "no";
            cell.innerText = text;
        });
    }

    // TODO: subTables flickers
    handleRowSelected(event) {
        // bubbled up event from datatable-table
        const row_id = parseInt(event.detail.value);
        const indexToItem = this.selectedRows ? this.selectedRows.indexOf(row_id) : -1;

        this.copyButton = false;
        this.updateButton = false;
        this.deleteButton = false;
        this.viewerButton = false;

        if (indexToItem === -1) {
            if(!this.multiSelect) {
                this.selectedRows = [];

                if(this.copyButtonInit && store.get("user.Role.CreateLevel") >= this.securityLevel.createLevel) this.copyButton = true;
                if(this.updateButtonInit && store.get("user.Role.UpdateLevel") >= this.securityLevel.updateLevel) this.updateButton = true;
                if(this.deleteButtonInit && store.get("user.Role.DeleteLevel") >= this.securityLevel.deleteLevel) this.deleteButton = true;

                if("viewer" in this.gridTables[0] && this.gridTables[0].viewer &&
                    store.get("user.Role.RunLevel") >= this.securityLevel.runLevel) {
                    this.viewerButton = true;
                }
                if(!this.copyButton && !this.updateButton && !this.deleteButton && !this.viewerButton) return false;
            }
            this.selectedRows.push(row_id);
        } else {
            this.selectedRows.splice(indexToItem, 1);
        }

        this.saveGridState();

        this.table.selectedRows = this.selectedRows;
        // form component
        if(this.name && this.ownerId) {
            this.setFormData();
        }
        // Mutating an object or array doesn't change the object reference, so it won't trigger an update
        this.table.requestUpdate(); // force update
    }

    handleRowOpened(event) {
        // bubbled up event from datatable-table
        this.openRows = event.detail.value;

        this.programStack = [];  // initialize program stack

        this.saveGridState();
        // Mutating an object or array doesn't change the object reference, so it won't trigger an update
        this.table.requestUpdate(); // force update
    }

    handleTabSelect(event) {
        // bubbled up event from datatable-table
        this.tabSelect = event.detail.value;
        this.saveGridState();
    }

    // TODO: subTables flickers
    handleSortColumn(event) {
        // bubbled up event from datatable-table
        this.gridColumns = event.detail.value;
        this.saveGridState();

        this.getGridData();
        this.table.gridData = this.gridData;
        this.table.gridColumns = this.gridColumns;
    }

    // TODO: subTables flickers
    handleDropColumn(event) {
        // bubbled up event from datatable-table
        this.gridColumns = event.detail.value;
        this.saveGridState();

        this.table.gridColumns = this.gridColumns;
        // Mutating an object or array doesn't change the object reference,
        // so it won't trigger an update
        this.table.requestUpdate(); // force update
    }

    // TODO: subTables flickers
    handleRowsPerPageChange(event) {
        // bubbled up event from datatable-footer
        this.rowsPerPage = event.detail.value;

        this.saveGridState();

        if(this.gridColumns) {
            this.getGridData();
            this.table.gridData = this.gridData;
        }
    }

    handlePageChange(event) {
        // bubbled up event from datatable-pagination
        this.currentPage = event.detail.value;

        this.saveGridState();

        if(this.gridColumns) {
            this.getGridData();
            this.table.gridData = this.gridData;
        }
    }

    // ui-stepper parent
    handleStepperBack(event, panel, stepperData, activeStep, totalSteps) {
        if(this.backHandler) {
            const myFunction = window[this.backHandler];
            if (isFunction(myFunction)) {
                return myFunction(event, panel, stepperData, activeStep, totalSteps);
            }
        } else if(this.parentBackHandler) {
            return this.parentBackHandler(event, panel, stepperData, activeStep, totalSteps);
        }
        return true;
    }

    // ui-stepper parent
    handleStepperNext(event, panel, stepperData, activeStep, totalSteps) {
        if(!this.validate()) return false;

        if(activeStep === totalSteps)  {
            if(this.submitHandler) {
                const myFunction = window[this.submitHandler];
                if (isFunction(myFunction)) {
                    return myFunction(event, this.formData);
                }
            }
        } else if(this.nextHandler) {
            const myFunction = window[this.nextHandler];
            if (isFunction(myFunction)) {
                return myFunction(event, panel, stepperData, activeStep, totalSteps,
                                    this.selectedRows);
            }
        } else if(this.parentNextHandler) {
            return this.parentNextHandler(event, panel, stepperData, activeStep,
                                        totalSteps, this.selectedRows);
        }
        return true;
    }

    // ui-stepper parent
    handleStepperStep(panel, step, stepperData, activeStep, totalSteps) {
        if(this.stepHandler) {
            const myFunction = window[this.stepHandler];
            if (isFunction(myFunction)) {
                return myFunction(panel, stepperData, activeStep, totalSteps);
            }
        } else if(this.parentStepHandler) {
            return this.parentStepHandler(panel, stepperData, activeStep, totalSteps);
        }
        if(step > activeStep) {
            if(!this.validate()) return false;
        }
        return true;
    }

    // called by parent form panel
    validate() {
        if(this.owner && this.owner.tagName === "FORM-PANEL") {
            return this.owner.validate(true); // force validate
        }

        if(!isNull(this.min)) {
            if(this.multiSelect && this.allRowsSelected) {
                if(this.totalRows < this.min) return false;
            }
            if(this.selectedRows.length < this.min) return false;
        }
        if(!isNull(this.max)) {
            if(this.multiSelect && this.allRowsSelected) {
                if(this.totalRows > this.max) return false;
            }
            if(this.selectedRows.length > this.max) return false;
        }
        return true;
    }

    // called by parent form panel
    updateData(name) {
        let rows = [];
        if(this.inputDataSelect)  rows = this.selectedRows;
        else rows = this.gridData;

        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: {
                        key: name,
                        value: rows,
                        sender: [`${this.instanceId}.updateData`]
                    }
        }));
    }

    // datatable as a form component - setFieldValue from form
    setFieldValue(value) {
        if(!isEmpty(value) && isArray(value)) {
            let ok = false;
            if(this.inputDataSelect) {
                if(this.multiSelect && value[0] === "All") {
                    this.allRowsSelected = true;
                }
                else {
                    this.allRowsSelected = false;
                    this.selectedRows = value;
                }
                ok = true;
            } else {
                this.gridData = value;
                this.totalRows = value.length;
                ok = true;
            }
            if(ok) this.requestUpdate();  // force render
        }
    }
    // form component
    setFormData() {
        if(this.name && this.ownerId) {
            // bubble up event to parent Lit form
            this.value = [];
            if(this.allRowsSelected) {
                this.value = ["All"]; // to pass min validation
            }
            else {
                if(this.inputDataSelect)  this.value = this.selectedRows;
                else  this.value = this.gridData;
            }

            this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    key: this.name,
                    value: this.value,
                    type: this.fieldType,
                    fieldType: this.fieldType,
                    field: this,
                    record: null,
                    sender: [`${this.instanceId}.setFormData`]
                }
            }));
            // force form to validate
            this.dispatchEvent(new CustomEvent(`form-field-blur-${this.ownerId}`, {
                    bubbles: true,
                    composed: true
            }));
        }
    }
    // form component with listeners
    setListeners(listeners, formData) {
        for(const listen of listeners) {
            const value = get(formData, listen.field, null);
            if(value) {
                switch(listen.event) {
                    case "criteria":
                        this.criteria = value;
                        break;
                    case "criteria_type":
                        this.criteriaType = value;
                        break;
                    case "selected_rows":
                        this.selectedRows = value;
                        break;
                    case "selected_all":
                        this.allRowsSelected = value;
                }
            }
        }
        if(this.dbTable) {
            if(!isEmpty(this.gridColumns) && !this.inputDataGrid) {
                this.getGridData(null, null, true);
            }
        }
    }

    updated() {
        if(this.table === null)
            this.table = this.shadowRoot.querySelector("datatable-table");
        if(this.columns === null)
            this.columns = this.shadowRoot.querySelector("datatable-columns");
        if(this.header === null)
            this.header = this.shadowRoot.querySelector("datatable-header");
        if(this.footer === null)
            this.footer = this.shadowRoot.querySelector("datatable-footer");
        if(this.collapse === null)
            this.collapse = this.shadowRoot.querySelector(".collapse");

        // check if auto-refresh is on and not running
        if(this.autoRefresh && isNil(this.timerId)) this.setAutoRefreshTimer();

        // where datatable is a form component
        if(this.footer && this.name && this.ownerId) {
            const error_box = this.footer.shadowRoot.querySelector("[data-error]");
            if(error_box) {
                if(this.errorMessage) {
                    error_box.textContent = this.errorMessage;
                    error_box.classList.remove("hidden");
                } else {
                    error_box.textContent = "";
                    error_box.classList.add("hidden");
                }
            }
        }
    }

    shouldUpdate(changedProperties) {
        // check if can render
        if(isNil(this.gridColumns)) return false;
        else return true;
    }

    getData() {
        if(this.owner) return this.owner.getData();

        return this.gridData;
    }

    reload() {
        // called by owner form
        // called by ui-step - fetch-data ui-step
        this.getGridData();
    }

    render() {
        const loader = this.gridTables[0]["loader"] || {};
        let addButton = this.addButton;
        let addButtonInit = this.addButtonInit;
        let copyButton = this.copyButton;
        let copyButtonInit = this.copyButtonInit;
        let updateButton = this.updateButton;
        let updateButtonInit = this.updateButtonInit;
        let uploadImageButton = this.uploadImageButton;
        let loaderButtonTooltip = null;
        if(!isEmpty(loader) && (addButton || updateButton)) {
            switch(loader.type) {
                case "uploadImage":
                    if(!isEmpty(this.selectedRows)) loaderButtonTooltip = "Update Image";
                    else loaderButtonTooltip = "Upload Image";
                    uploadImageButton = true;
                    break;
            }
            addButton = false;
            addButtonInit = false;
            copyButton = false;
            copyButtonInit = false;
            updateButton = false;
            updateButtonInit = false;
        }

        let viewerButtonTooltip = null;
        if(this.viewerButton) {
            viewerButtonTooltip = this.gridTables[0].viewer.tooltip;
        }

        if(this.ownerId) {
            let buttonText = this.nextButtonText;
            let mode = "Create";
            if(!isEmpty(this.selectedRows)) {
                buttonText = this.selectButtonText;
                mode = "Update";
            }
            if(this.formMode) {
                // if parent is ui-stepper or ui-form multiple
                this.dispatchEvent(new CustomEvent(`step-mode-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: {
                        mode: mode
                    }
                }));

                this.dispatchEvent(new CustomEvent(`submit-button-disable-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: {
                        value: !this.activeNextButton,
                        buttonText: buttonText
                    }
                }));
            }
            if(this.selectRow) {
                let data = {};
                if(!isEmpty(this.selectedRows)) {
                    // row data
                    data = this.gridData.find(item => item.Id === this.selectedRows[0]);
                } else {
                    // init row
                    this.gridColumns.forEach(obj => {
                        let value = "";
                        if(obj.textType === "Dict") value = {};
                        else if(obj.textType === "List") value = [];
                        else value = isEmpty(obj.default) ? "" : obj.default;
                        set(data, obj.name, value);
                    });
                }
                // if parent is ui-stepper or ui-form multiple
                this.dispatchEvent(new CustomEvent(`grid-select-row-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: {
                        key: this.name,
                        value: data,
                        sender: [`${this.instanceId}.render`]
                    }
                }));
            }
            // throw to grid event listeners - ie. ui-form
            this.dispatchEvent(new CustomEvent(`grid-events-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: [
                        {event: "criteria", value: this.criteria},
                        {event: "criteria_type", value: this.criteriaType},
                        {event: "selected_rows", value: this.selectedRows},
                        {event: "selected_all", value: this.allRowsSelected}
                    ]
            }));
        }

        return html`
            <div class="card w-full bg-base-100 shadow-xl overflow-y-auto">
                ${this.toolbar ? html`
                    <datatable-header
                        datatable-id="${this.instanceId}"
                        header-title="${this.title}"
                        total-crits="${this.criteria.length}"
                        total-secs="${this.autoRefresh ? this.refreshInterval : 0}"

                        .securityLevel="${this.securityLevel}"
                        .prependToolbar="${this.prependToolbar}"
                        .appendToolbar="${this.appendToolbar}"
                        .selectedRows="${this.selectedRows}"

                        loader-button-tooltip="${loaderButtonTooltip}"
                        viewer-button-tooltip="${viewerButtonTooltip}"

                        ?multiple="${this.multiSelect}"
                        ?all-rows-selected="${this.allRowsSelected}"
                        ?upload-image-button="${uploadImageButton}"
                        ?viewer-button="${this.viewerButton}"
                        ?add-button="${addButton && (isNil(this.crudMode) || this.crudMode === 'Create')}"
                        ?copy-button="${copyButton && (isNil(this.crudMode) || this.crudMode === 'Copy')}"
                        ?update-button="${updateButton && (isNil(this.crudMode) || this.crudMode === 'Update')}"
                        ?delete-button="${this.deleteButton && (isNil(this.crudMode) || this.crudMode === 'Delete')}"
                        ?filter-button="${this.filterButton}"
                        ?column-button="${this.columnButton}"
                        ?bookmark-button="${this.bookmarkButton}"
                        ?refresh-button="${this.refreshButton}"
                        ?auto-refresh-button="${this.autoRefreshButton}"
                        ?download-button="${this.downloadButton}"
                        ?print-button="${this.printButton}"

                        .gridOptions="${this.gridOptions}"
                    ></datatable-header>`
                : nothing}
                <div class="card-body" style="padding-top: 5px; padding-bottom: 10px;">
                    <div tabindex="0" class="collapse bg-base-100 overflow-auto">
                        <div class="collapse-content">
                            <ui-container></ui-container>
                        </div>
                    </div>
                    <datatable-table
                        datatable-id="${this.instanceId}"
                        panel-table="${this.dbTable}"

                        .programStack="${this.programStack}"
                        .gridColumns="${this.gridColumns}"
                        .gridTables="${this.gridTables}"
                        .gridData="${this.gridData}"
                        .selectedRows="${this.selectedRows}"
                        .openRows="${this.openRows}"
                        .securityLevel="${this.securityLevel}"

                        .preSubTables="${this.preSubTables}"
                        .postSubTables="${this.postSubTables}"

                        program="${this.program}"
                        tab-select="${this.tabSelect}"
                        ?multiple="${this.multiSelect}"
                        ?local-data="${this.localData}"
                        ?all-rows-selected="${this.allRowsSelected}"
                        ?upload-image-button="${uploadImageButton}"
                        ?viewer-button="${this.viewerButton}"
                        ?add-button="${addButtonInit}"
                        ?copy-button="${copyButtonInit}"
                        ?update-button="${updateButtonInit}"
                        ?delete-button="${this.deleteButtonInit}"
                        ?filter-button="${this.filterButton}"
                        ?column-button="${this.columnButton}"
                        ?bookmark-button="${this.bookmarkButton}"
                        ?refresh-button="${this.refreshButton}"
                        ?auto-refresh-button="${this.autoRefreshButton}"
                        ?download-button="${this.downloadButton}"
                        ?print-button="${this.printButton}"

                        .gridOptions="${this.gridOptions}"
                        .ownerId="${this.ownerId}"
                        .owner="${this.owner}"
                    ></datatable-table>
                    ${this.footbar ? html`
                        <datatable-footer
                            datatable-id="${this.instanceId}"
                            current-page="${this.currentPage}"
                            rows-per-page="${this.rowsPerPage}"
                            start-row="${this.startRow}"
                            total-rows="${this.totalRows}"

                            .gridOptions="${this.gridOptions}"
                        ></datatable-footer>`
                    : nothing}
                </div>
                <datatable-columns
                    datatable-id="${this.instanceId}"
                ></datatable-columns>
            </div>
        `;
    }
}

customElements.define("ui-datatable", Datatable)
