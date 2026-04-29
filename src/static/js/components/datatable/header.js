import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../css/tw.js'

import { isEmpty } from "../../utils"
import svg from "../../svg"
import "../../../icons/plus.js"
import "../../../icons/documentdups.js"
import "../../../icons/pencils.js"
import "../../../icons/trashs.js"
import "../../../icons/arrowuptray.js"
import "../../../icons/eyes.js"

class DatatableHeader extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        title: { attribute: "header-title", type: String },

        securityLevel: { type: Object },
        selectedRows: { type: Array },
        prependToolbar: { type: Array },
        appendToolbar: { type: Array },

        gridOptions: { type: Object },

        viewerButtonTooltip: { attribute: "viewer-button-tooltip", type: String },
        loaderButtonTooltip: { attribute: "loader-button-tooltip", type: String },

        multiSelect: { attribute: "multiple", type: Boolean },
        allRowsSelected: { attribute: "all-rows-selected", type: Boolean },
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

        totalCrits: { attribute: "total-crits", type: Number },
        totalSecs: { attribute: "total-secs", type: Number },
    };

    constructor() {
        super();

        this.title = null;

        this.loaderButtonTooltip = null;
        this.viewerButtonTooltip = null;

        this.gridOptions = null;

        this.multiSelect = false;
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

        this.totalCrits = 0;
        this.totalSecs = 0;

        this.prependToolbar = [];
        this.appendToolbar = [];
        this.selectedRows = [];

        this.securityLevel = {
            "runLevel": 9999,
            "createLevel": 9999,
            "updateLevel": 9999,
            "deleteLevel": 9999
        };
    }

    async connectedCallback() {
        super.connectedCallback();

        if(!isEmpty(this.gridOptions)) {
            if("title" in this.gridOptions) this.title = this.gridOptions.title;
        }
    }

    onSelectAll(event) {
        this.allRowsSelected = !this.allRowsSelected;
        this.dispatchEvent(new CustomEvent(`grid-select-all-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: {
                value: this.allRowsSelected
            }
        }));
    }

    onUploadImage(event) {
        this.dispatchEvent(new CustomEvent(`grid-upload-image-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onViewer(event) {
        this.dispatchEvent(new CustomEvent(`grid-viewer-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onAdd(event) {
        this.dispatchEvent(new CustomEvent(`grid-add-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onCopy(event) {
        this.dispatchEvent(new CustomEvent(`grid-copy-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onUpdate(event) {
        this.dispatchEvent(new CustomEvent(`grid-update-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onDelete(event) {
        this.dispatchEvent(new CustomEvent(`grid-delete-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onFilter(event) {
        this.dispatchEvent(new CustomEvent(`grid-filter-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onColumns(event) {
        this.dispatchEvent(new CustomEvent(`grid-columns-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onBookmark(event) {
        this.dispatchEvent(new CustomEvent(`grid-bookmark-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onRefresh(event) {
        this.dispatchEvent(new CustomEvent(`grid-refresh-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onAutoRefresh(event) {
        this.dispatchEvent(new CustomEvent(`grid-auto-refresh-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    onCopyToClipboard(event) {
        this.dispatchEvent(new CustomEvent(`grid-copy-to-clipboard-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));

        // close dropdown
        const ul = event.target.closest("ul");
        ul.blur();
    }

    onDownloadPDF(event) {
        this.dispatchEvent(new CustomEvent(`grid-download-pdf-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
        // close dropdown
        const ul = event.target.closest("ul");
        ul.blur();
    }

    onDownloadExcel(event) {
        this.dispatchEvent(new CustomEvent(`grid-download-excel-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
        // close dropdown
        const ul = event.target.closest("ul");
        ul.blur();
    }

    onDownloadCSV(event) {
        this.dispatchEvent(new CustomEvent(`grid-download-csv-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
        // close dropdown
        const ul = event.target.closest("ul");
        ul.blur();
    }

    onPrint(event) {
        this.dispatchEvent(new CustomEvent(`grid-print-${this.datatableId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    firstUpdated() {
        svg.render(this.shadowRoot);
    }


    render() {
        const crits = this.totalCrits > 99 ? "99+" : this.totalCrits.toString();
        const secs = this.totalSecs > 99 ? "99+" : this.totalSecs.toString();
        return html`
            <div class="navbar bg-base-100 flex justify-between items-center">
                <div class="flex items-center gap-x-5">
                    ${this.title ?
                        html`<h2 class="card-title">${this.title}</h2>`
                    : nothing}
                </div>
                <div class="flex items-center gap-x-2">
                    ${this.prependToolbar.map((tool) => {
                        return tool(this.selectedRows.length === 1);
                    })}
                    ${this.multiSelect ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Select All Rows">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;">
                                    <input type="checkbox"
                                        ?checked="${this.allRowsSelected}"
                                        class="checkbox checkbox-sm"
                                    @click="${this.onSelectAll}"></input>
                                </button>
                            </div>`
                    : nothing}
                    ${this.viewerButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="${this.viewerButtonTooltip}">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onViewer}">
                                    <icon-eyes></icon-eyes>
                                </button>
                            </div>`
                    : nothing}
                    ${this.uploadImageButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="${this.loaderButtonTooltip}">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onUploadImage}">
                                    <icon-arrowuptray></icon-arrowuptray>
                                </button>
                            </div>`
                    : nothing}
                    ${this.addButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="New">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onAdd}">
                                    <icon-plus></icon-plus>
                                </button>
                            </div>`
                    : nothing}
                    ${this.copyButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Copy">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onCopy}">
                                    <icon-documentdups></icon-documentdups>
                                </button>
                            </div>`
                    : nothing}
                    ${this.updateButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Edit">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onUpdate}">
                                    <icon-pencils></icon-pencils>
                                </button>
                            </div>`
                    : nothing}
                    ${this.deleteButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Delete">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onDelete}">
                                    <icon-trashs></icon-trashs>
                                </button>
                            </div>`
                    : nothing}
                    ${this.filterButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Filter">
                                <div class="indicator">
                                    ${crits !== "0" ?
                                        html`
                                            <span class="indicator-item badge badge-secondary text-white z-[25]">${crits}</span>
                                        `
                                    : html``
                                    }
                                    <button class="btn btn-ghost rounded-full"
                                        style="padding: 8px; height: inherit; min-height: inherit;"
                                        @click="${this.onFilter}">
                                        <span data-icon>filterlist</span>
                                    </button>
                                </div>
                            </div>`
                    : nothing}
                    ${this.columnButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Columns">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onColumns}">
                                    <span data-icon>viewcolumnss</span>
                                </button>
                            </div>`
                    : nothing}
                    ${this.bookmarkButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Bookmark">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onBookmark}">
                                    <span data-icon>bookmarks</span>
                                </button>
                            </div>`
                    : nothing}
                    ${this.refreshButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Refresh">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onRefresh}">
                                    <span data-icon>refresh</span>
                                </button>
                            </div>`
                    : nothing}
                    ${this.autoRefreshButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Auto Refresh">
                                <div class="indicator">
                                    ${secs !== "0" ?
                                        html`
                                            <span class="indicator-item badge badge-secondary text-white z-[25]">${secs}</span>
                                        `
                                    : html``
                                    }
                                    <button class="btn btn-ghost rounded-full"
                                        style="padding: 8px; height: inherit; min-height: inherit;"
                                        @click="${this.onAutoRefresh}">
                                        <span data-icon>history</span>
                                    </button>
                                </div>
                            </div>`
                    : nothing}
                    ${this.downloadButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Download">
                                <div class="dropdown dropdown-end">
                                    <label tabindex="0" class="btn btn-ghost rounded-full"
                                        style="padding: 8px; height: inherit; min-height: inherit;">
                                        <span data-icon>cloudarrowdowns</span>
                                    </label>
                                    <ul tabindex="0"
                                        class="block dropdown-content z-[50] menu p-2 shadow bg-base-200 text-base-content rounded-box w-max">
                                        <li><a
                                            @click="${this.onCopyToClipboard}">
                                            <span data-icon>clipboard</span>
                                            Copy To Clipboard
                                        </a></li>
                                        <li><a
                                            @click="${this.onDownloadPDF}">
                                            <span data-icon>filepdfo</span>
                                            Download as PDF
                                        </a></li>
                                        <li><a
                                            @click="${this.onDownloadExcel}">
                                            <span data-icon>fileexcelo</span>
                                            Download as Excel
                                        </a></li>
                                        <li><a
                                            @click="${this.onDownloadCSV}">
                                            <span data-icon>filetexto</span>
                                            Download as CSV
                                        </a></li>
                                    </ul>
                                </div>
                            </div>`
                    : nothing}
                    ${this.printButton ?
                        html`<div class="tooltip tooltip-bottom z-[10]" data-tip="Print">
                                <button class="btn btn-ghost rounded-full"
                                    style="padding: 8px; height: inherit; min-height: inherit;"
                                    @click="${this.onPrint}">
                                    <span data-icon>printers</span>
                                </button>
                            </div>`
                    : nothing}
                    ${this.appendToolbar.map((tool) => {
                        return tool(this.selectedRows.length === 1);
                    })}
                </div>
            </div>
        `;
    }
}

customElements.define("datatable-header", DatatableHeader)
