import { LitElement, html, css } from 'lit'

import { isNil } from "../../utils"

class Script extends LitElement {
    static styles = [
        css `
            :host{
                height: 100%;
                width: 100%;
                overflow: auto;
            }
        `
    ];

    static instanceCounter = 0;

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        title: { attribute: "script-title", type: String },
        program: { type: String },
        path: { type: String },
        component: { type: String },

        module: { state: true }
    };

    constructor() {
        super();
        this.instanceId = "Script-" + (++Script.instanceCounter).toString();

        this.ownerId = null;
        this.title = "";
        this.program = null;
        this.path = null;
        this.component = null;

        this.module = null;
    }

    async connectedCallback() {
        super.connectedCallback();

        try {
            /* webpack limits dynamic import - to overcome limitation
                hard code a partial import path ie. "/scripts/"
                that is from public src/static
            */
            this.module = await import(`/scripts/${this.path}`);
        } catch (err) {
            const message = `${err.status}  ${err.detail} : script.connectedCallback path: ${this.path}`;
            console.log(message);
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    shouldUpdate(changedProperties) {
        // check if can render
        if(isNil(this.module)) return false;
        else if(isNil(this.component)) return false;
        return true;
    }

    renderComponent() {
        const component = document.createElement(this.component);
        component.ownerId = this.ownerId;
        component.scriptId = this.instanceId;
        component.title = this.title;
        component.program = this.program;

        return component;
    }

    render() {
        return html`
            ${this.renderComponent()}
        `;
    }
}
customElements.define("ui-script", Script)
