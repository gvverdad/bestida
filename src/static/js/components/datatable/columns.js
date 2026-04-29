import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../../css/tw.js'


class DatatableColumns extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static instanceCounter = 0;

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        gridColumns: { attribute: "grid-columns", type: Object }
    };

    constructor() {
        super();
        this.instanceId = (++DatatableColumns.instanceCounter).toString();

        this.handleCloseDialog = this.handleCloseDialog.bind(this);
        this.onColChange = this.onColChange.bind(this);
        this.onLabelChange = this.onLabelChange.bind(this);

        this.gridColumns = null;
        this.dirty = false;
    }

    connectedCallback() {
        super.connectedCallback();

        this.instanceId = `DatatableColumns-${this.datatableId}-${this.instanceId}`;

        this.addEventListener(`dialog-close-${this.instanceId}`, this.handleCloseDialog);
    }

    disconnectedCallback() {
        super.disconnectedCallback();

        this.removeEventListener(`dialog-close-${this.instanceId}`, this.handleCloseDialog);
    }

    onColChange(event) {
        const index = parseInt(event.target.name);

        this.gridColumns.every((ele, idx) => {
            if(index === idx) {
                ele.options.display = event.target.checked;
                this.dirty = true;
                return false;  // to break out of loop
            }
            return true;
        });
    }

    onLabelChange(event) {
        const index = parseInt(event.target.name.split("_label_")[1]);

        this.gridColumns.every((ele, idx) => {
            if(index === idx) {
                ele.column_label = event.target.value;
                this.dirty = true;
                return false;  // to break out of loop
            }
            return true;
        });
    }

    handleCloseDialog(event) {
        this.dispatchEvent(new CustomEvent(`grid-columns-update-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: {
                value: this.gridColumns,
                dirty: this.dirty
            }
        }));
        this.gridColumns = null;
    }

    show() {
        this.dirty = false;
        const dialog = this.shadowRoot.querySelector("ui-dialog");
        dialog.showModal();
    }

    render() {
        const columns = this.gridColumns ? this.gridColumns : [];
        // readonly is not supported for <input type="checkbox">
        return html`
            <ui-dialog owner-id="${this.instanceId}">
                <table class="table table-pin-rows table-auto">
                    <caption class="caption-top font-semibold">
                        Select Columns/Change Labels to Display
                    </caption>
                    <thead>
                        <tr class="bg-base-300 h-10">
                            <th class="align-middle text-sm font-semibold">Columns</th>
                            <th class="align-middle text-sm font-semibold">Label</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${columns.map((column, index) =>
                            html`
                                <tr class="hover h-10 bg-base-100 text-content">
                                    <td>
                                        <label class="cursor-pointer font-medium label" style="justify-content: start;">
                                            <input type="checkbox"
                                                name="${index}"
                                                class="toggle toggle-sm toggle-primary me-1 focus:outline-none focus:border-primary"
                                                ?checked="${column.options.display}"
                                                ?disabled="${column.sticky}"
                                                @change="${this.onColChange}">
                                            </input>
                                            <span class="label-text">${column.label}</span>
                                        </label>
                                    </td>
                                    <td>
                                        <input type="text"
                                            name="${`${column.name}_label_${index}`}"
                                            value="${column.column_label}"
                                            class="input input-bordered w-full max-w-3xl focus:outline-none focus:border-primary"
                                            @change="${this.onLabelChange}">
                                        </input>
                                    </td>
                                </tr>
                            `
                        )}
                    </tbody>
                </table>
            </ui-dialog>
        `;
    }
}

customElements.define("datatable-columns", DatatableColumns)
