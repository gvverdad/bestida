import { LitElement, html, css } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../../css/tw.js'

import svg from "../../svg"
import "../../../icons/ellipsish.js"

export class DatatablePagination extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        rowsPerPage: { attribute: "rows-per-page", type: Number },
        currentPage: { attribute: "current-page", type: Number},
        totalRows: { attribute: "total-rows", type: Number},

        totalPages: { state: true },
    };

    constructor() {
        super();

        this.rowsPerPage = 0;
        this.currentPage = 1;
        this.totalRows = 0;

        this.totalPages = 0;
    }

    async connectedCallback() {
        super.connectedCallback();

        if(this.totalRows > 0) {
            if(this.rowsPerPage < 0) this.totalPages = 1;
            else this.totalPages = Math.ceil(this.totalRows / this.rowsPerPage);
        }
        if(this.totalRows > 0 && this.currentPage > this.totalPages) {
            this.currentPage = 1;
            this.handleChangePage(this.currentPage);
        }
    }

    firstUpdated() {
        svg.render(this.shadowRoot);
    }

    onPageChange(event) {
        this.currentPage = parseInt(event.target.textContent);
        this.handleChangePage(this.currentPage);
    }

    handleChangePage(page) {
        this.dispatchEvent(new CustomEvent(`grid-page-change-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: { value: page }
        }));
    }

    onNextPage(event) {
        if(this.currentPage === this.totalPages) return false;

        this.currentPage += 1;
        this.handleChangePage(this.currentPage);
    }

    onPreviousPage(event) {
        if(this.currentPage === 1) return false;

        this.currentPage -= 1;
        this.handleChangePage(this.currentPage);
    }

    updated() {
        if(this.totalRows > 0) {
            if(this.rowsPerPage < 0) this.totalPages = 1;
            else this.totalPages = Math.ceil(this.totalRows / this.rowsPerPage);
        }
        if(this.totalRows > 0 && this.currentPage > this.totalPages) {
            this.currentPage = 1;
            this.handleChangePage(this.currentPage);
        }
    }

    render() {
        const pageTemplate = [];
        if(this.totalRows > 0) {
            if(this.totalPages <= 7) {
                for (let page = 1; page < this.totalPages + 1; page++) {
                    const classes = {
                        "bg-primary": page === this.currentPage,
                        "shadow-md":  page === this.currentPage,
                        "hover:border": page != this.currentPage,
                        "hover:bg-base-300": page != this.currentPage,
                    };
                    pageTemplate.push(html`
                        <li>
                            <a @click="${this.onPageChange}"
                                class="${classMap(classes)} cursor-pointer mx-1 flex h-8 w-8 items-center justify-center rounded-full p-0 text-sm transition duration-150 ease-in-out hover:border hover:bg-base-300">
                                ${page}
                            </a>
                        </li>
                    `);
                }
            } else {
                let classes = {
                    "bg-primary": this.currentPage === 1,
                    "shadow-md":  this.currentPage === 1,
                    "hover:border": this.currentPage != 1,
                    "hover:bg-base-300": this.currentPage != 1,
                };
                pageTemplate.push(html`
                    <li>
                        <a @click="${this.onPageChange}"
                            class="${classMap(classes)} cursor-pointer mx-1 flex h-8 w-8 items-center justify-center rounded-full p-0 text-sm transition duration-150 ease-in-out">
                            1
                        </a>
                    </li>
                `);
                if((this.currentPage - 1) < 4) {
                    for (let page = 2; page < Math.min(6,this.totalPages); page++) {
                        const classes = {
                            "bg-primary": page === this.currentPage,
                            "shadow-md":  page === this.currentPage,
                            "hover:border": page != this.currentPage,
                            "hover:bg-base-300": page != this.currentPage,
                        };
                        pageTemplate.push(html`
                            <li>
                                <a @click="${this.onPageChange}"
                                    class="${classMap(classes)} cursor-pointer mx-1 flex h-8 w-8 items-center justify-center rounded-full p-0 text-sm transition duration-150 ease-in-out hover:border hover:bg-base-300">
                                    ${page}
                                </a>
                            </li>
                        `);
                    }
                    pageTemplate.push(html`
                        <li class="flex items-end">
                            <icon-ellipsish><icon-ellipsish>
                        </li>
                    `);
                } else if((this.totalPages - this.currentPage) < 4) {
                    pageTemplate.push(html`
                        <li class="flex items-end">
                            <icon-ellipsish><icon-ellipsish>
                        </li>
                    `);
                    for (let page = this.totalPages - 4; page < this.totalPages; page++) {
                        const classes = {
                            "bg-primary": page === this.currentPage,
                            "shadow-md":  page === this.currentPage,
                            "hover:border": page != this.currentPage,
                            "hover:bg-base-300": page != this.currentPage,
                        };
                        pageTemplate.push(html`
                            <li>
                                <a @click="${this.onPageChange}"
                                    class="${classMap(classes)} cursor-pointer mx-1 flex h-8 w-8 items-center justify-center rounded-full p-0 text-sm transition duration-150 ease-in-out hover:border hover:bg-base-300">
                                    ${page}
                                </a>
                            </li>
                        `);
                    }
                } else {
                    pageTemplate.push(html`
                        <li class="flex items-end">
                            <icon-ellipsish><icon-ellipsish>
                        </li>
                    `);
                    for (let page = this.currentPage - 1; page < this.currentPage + 2; page++) {
                        const classes = {
                            "bg-primary": page === this.currentPage,
                            "shadow-md":  page === this.currentPage,
                            "hover:border": page != this.currentPage,
                            "hover:bg-base-300": page != this.currentPage,
                        };
                        pageTemplate.push(html`
                            <li>
                                <a @click="${this.onPageChange}"
                                    class="${classMap(classes)} cursor-pointer mx-1 flex h-8 w-8 items-center justify-center rounded-full p-0 text-sm transition duration-150 ease-in-out hover:border hover:bg-base-300">
                                    ${page}
                                </a>
                            </li>
                        `);
                    }
                    pageTemplate.push(html`
                        <li class="flex items-end">
                            <icon-ellipsish><icon-ellipsish>
                        </li>
                    `);
                }
                classes = {
                    "bg-primary": this.totalPages === this.currentPage,
                    "shadow-md":  this.totalPages === this.currentPage,
                    "hover:border": this.totalPages != this.currentPage,
                    "hover:bg-base-300": this.totalPages != this.currentPage,
                };
                pageTemplate.push(html`
                    <li>
                        <a @click="${this.onPageChange}"
                            class="${classMap(classes)} cursor-pointer mx-1 flex h-8 w-8 items-center justify-center rounded-full p-0 text-sm transition duration-150 ease-in-out">
                            ${this.totalPages}
                        </a>
                    </li>
                `);
            }
        }

        const prevClass = {
            "cursor-pointer": this.currentPage > 1,
            "hover:border": this.currentPage > 1,
            "hover:bg-base-300": this.currentPage > 1,
        };
        const nextClass = {
            "cursor-pointer": this.currentPage < this.totalPages,
            "hover:border": this.currentPage < this.totalPages,
            "hover:bg-base-300": this.currentPage < this.totalPages,
        };

        return html`
            <nav>
                <ul class="flex">
                    <li>
                        <a @click="${this.onPreviousPage}"
                            class="${classMap(prevClass)} mx-1 flex h-8 w-8 items-center justify-center rounded-full bg-base-100 p-0 text-sm transition duration-150 ease-in-out">
                            <span data-icon>chevronleft</span>
                        </a>
                    </li>
                    ${pageTemplate}
                    <li>
                        <a @click="${this.onNextPage}"
                            class="${classMap(nextClass)} mx-1 flex h-8 w-8 items-center justify-center rounded-full bg-base-100 p-0 text-sm transition duration-150 ease-in-out">
                            <span data-icon>chevronright</span>
                        </a>
                    </li>
                </ul>
            </nav>
        `;
    }
}

customElements.define("datatable-pagination", DatatablePagination)
