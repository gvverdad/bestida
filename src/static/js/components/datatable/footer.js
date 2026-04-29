import { LitElement, html, css } from 'lit'
import { TWStyles } from '../../../css/tw.js'

import { isEmpty } from "../../utils"
import "./pagination"

class DatatableFooter extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        rowsPerPage: { attribute: "rows-per-page", type: Number },
        rowsPerPageOption: { attribute: "rows-per-page-options", type: Array },

        startRow: { attribute: "start-row", type: Number},
        totalRows: { attribute: "total-rows", type: Number},
        currentPage: { attribute: "current-page", type: Number},

        gridOptions: { type: Object },
    };

    constructor() {
        super();
        this.onChangeRowsPerPage = this.onChangeRowsPerPage.bind(this);

        this.gridOptions = null;

        this.startRow = 0;
        this.totalRows = 0;
        this.currentPage = 1;
        this.rowsPerPage = 10;
        this.rowsPerPageOption = [5, 10, 15, 20, 30, 50, 100, { label: 'All', value: -1 }];
    }

    async connectedCallback() {
        super.connectedCallback();

        if(this.currentPage === 0)  this.currentPage = 1;

        if(!isEmpty(this.gridOptions)) {
            if("rowsPerPage" in this.gridOptions) this.rowsPerPage = this.gridOptions.rowsPerPage;
            if("rowsPerPageOption" in this.gridOptions) this.rowsPerPageOption = this.gridOptions.rowsPerPageOption;
        }
    }

    onChangeRowsPerPage(event) {
        this.dispatchEvent(new CustomEvent(`grid-rows-per-page-change-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: { value: event.target.value }
        }));
    }

    render() {
        const rowsOptions = [];
        this.rowsPerPageOption.forEach((option, index) => {
            if(typeof option === "object") {
                rowsOptions.push(html`
                    <option value="${option.value}">${option.label}</option>
                `);
            } else {
                rowsOptions.push(html`
                    <option value="${option}" ?selected=${this.rowsPerPage === option} >${option}</option>
                `);
            }
        });
        const startRow = this.totalRows === 0 ? 0 : (this.currentPage - 1) * this.rowsPerPage + 1;
        const endRow = this.totalRows === 0 ? 0 : Math.min(this.totalRows, this.currentPage * this.rowsPerPage);
        return html`
            <div class="card-actions flex justify-between items-center gap-x-2">
                <div>
                    <span data-error
                        class="hidden block mt-2 text-sm text-red-500 peer-[&:not(:placeholder-shown):not(:focus):invalid]:block">
                    </span>
                </div>
                <div class="flex justify-end items-center gap-x-2">
                    <div class="flex items-center gap-x-1">
                        <div>
                            <label class="label text-sm font-medium leading-6"
                                for="rowsPerPage">
                                <span class="label-text">Rows per page:</span>
                            </label>
                        </div>
                        <div>
                            <select name="rowsPerPage"
                                @change="${this.onChangeRowsPerPage}"
                                class="select select-ghost w-fit max-w-xs">
                                ${rowsOptions}
                            </select>
                        </div>
                    </div>
                    <div>
                        <p>${startRow}-${endRow} of ${this.totalRows}</p>
                    </div>
                    <div>
                        <datatable-pagination
                            datatable-id="${this.datatableId}"
                            rows-per-page="${this.rowsPerPage}"
                            total-rows="${this.totalRows}"
                            current-page="${this.currentPage}"
                        ></datatable-pagination>
                    </div>
                </div>
            </div>
        `;
    }
}

customElements.define("datatable-footer", DatatableFooter)
