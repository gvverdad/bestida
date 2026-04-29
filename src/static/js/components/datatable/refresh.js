import { LitElement, html, css } from 'lit'
import { TWStyles } from '../../../css/tw.js'

class DatatableAutoRefresh extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static properties = {
        datatableId: { attribute: "datatable-id", type: String },
        interval: { type: Number },
        enable: { attribute: "auto-refresh", type: Boolean },
        intervalOptions: { attribute: "interval-options", type: Array },
    };

    constructor() {
        super();
        this.onApplyAuto = this.onApplyAuto.bind(this);
        this.onIntervalChange = this.onIntervalChange.bind(this);
        this.onEnableClick = this.onEnableClick.bind(this);

        this.interval = 60;
        this.enable = false;
        this.intervalOptions = [10, 15, 20, 25, 30, 45, 60, 90, 120, 180, 300];
    }

    onApplyAuto(event) {
        this.dispatchEvent(new CustomEvent(`grid-apply-auto-refresh-${this.datatableId}`, {
            bubbles: true,
            composed: true,
            detail: {
                interval: this.interval,
                enable: this.enable
            }
        }));
    }

    onIntervalChange(event) {
        this.interval = event.target.value;
    }

    onEnableClick(event) {
        this.enable = event.target.checked;
    }

    render() {
        return html`
            <div class="card bg-base-100 shadow-xl">
                <div class="card-body">
                    <div class="flex w-1/2 justify-between items-center">
                        <label class="cursor-pointer label font-medium">
                            <input type="checkbox"
                                   class="toggle toggle-sm toggle-primary me-1 focus:outline-none focus:border-primary"
                                   ?checked="${this.enable}"
                                   @click="${this.onEnableClick}"
                            ></input>
                            <span class="label-text">Auto Refresh</span>
                        </label>
                        <label class="cursor-pointer label font-medium">
                            <span class="label-text pr-3">Refresh Interval in Seconds</span>
                            <select @change="${this.onIntervalChange}"
                                class="select select-ghost w-fit"
                            >
                                ${this.intervalOptions.map((opt) =>
                                    html`
                                        <option value="${opt}"
                                            ?selected="${this.interval === opt}">
                                        ${opt}</option>
                                    `
                                )}
                            </select>
                        </label>
                        <button
                            @click="${this.onApplyAuto}"
                            class="btn btn-primary"
                        >Apply</button>
                    </div>
                </div>
            </div>
        `;
    }
}

customElements.define("datatable-auto-refresh", DatatableAutoRefresh)
