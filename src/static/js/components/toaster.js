import { LitElement, html, css } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../css/tw.js'

import "../../icons/x.js"

class Toaster extends LitElement {
    static styles = [css ``, TWStyles];

    static properties = {
        timeout: { type: Number },

        message: { state: true },
        alert: { state: true },
        timeoutId: { state: true },
    };

    constructor() {
        super();

        this.alert = "error";
        this.message = "";
        this.timeoutId = null;
        this.timeout = 5000; // default if timeout not defined in html attribute
    }

    connectedCallback() {
        super.connectedCallback();

        this.style.display = 'none';
    }

    show(message, alert = "error") {
        this.message = message;
        this.alert = alert;

        this.style.display = 'block';

        this.timeoutId = setTimeout(() => {
            this.hide();
        }, this.timeout);
    }

    onHide(event) {
        if(this.timeoutId) clearTimeout(this.timeoutId);
        this.hide();
    }

    hide() {
        this.style.display = 'none';

        this.alert = "error";
        this.message = "";
        this.timeoutId = null;
    }

    render() {
        const classes = {
            "alert-info": this.alert.toLowerCase() === "info",
            "alert-success": this.alert.toLowerCase() === "success",
            "alert-warning": this.alert.toLowerCase() === "warning",
            "alert-error": this.alert.toLowerCase() === "error"
        };
        return html`
            <div class="toast toast-top toast-center" id="toaster">
                <div class="alert ${classMap(classes)} flex justify-between items-center" id="alert">
                    <span id="content">${this.message}</span>
                    <button type="button"
                        @click=${this.onHide}
                        class="btn btn-ghost btn-sm rounded-full flex items-center justify-center"
                        style="padding: 8px; height: inherit; min-height: inherit;"
                    >
                        <icon-x><icon-x>
                    </button>
                </div>
            </div>
        `;
    }
}

customElements.define("ui-toaster", Toaster)
