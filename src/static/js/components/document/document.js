import { LitElement, html, css } from 'lit'

import api from "../../api"
import { isNil, isNull, isEmpty } from "../../utils"

class Document extends LitElement {
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
        title: { attribute: "label", type: String },

        program: { attribute: "program", type: String },
        programStack: { attribute: "program-stack", type: Array },
        props: { attribute: "params", type: Object },

        module: { state: true }
    };

    constructor() {
        super();
        this.instanceId = "Document-" + (++Document.instanceCounter).toString();

        this.ownerId = null;
        this.title = "";
        this.path = null;
        this.program = null;
        this.programStack = [];
        this.component = null;
        this.props = null;

        this.document = null;
        this.module = null;
    }

    async connectedCallback() {
        super.connectedCallback();
        try {
            await api.GET(`/getProgram/${this.program}/Document/1`, null)
                .then(async data => {
                    this.path = data.data.Path;
                    this.component = data.data.Component;

                    /* webpack limits dynamic import - to overcome limitation
                        hard code a partial import path ie. "/documents/"
                        that is from public src/static
                    */
                    this.module = await import(`/documents/${this.path}`);
            });
        } catch (err) {
            const message = `${err.status}  ${err.detail} : ui-document.connectedCallback ${this.program} path: ${this.path}`;
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
        this.document = document.createElement(this.component);

        if(!isEmpty(this.props)) {
            const schema = this.document.constructor.properties;
            for(const [key, value] of Object.entries(schema)) {
                if(key in this.props) {
                    this.document[key] = this.props[key];
                }
            }
        }
        this.document.ownerId = this.ownerId;
        this.document.documentId = this.instanceId;
        this.document.docuTitle = this.title;
        this.document.program = this.program;
        this.document.programStack = this.programStack;

        return this.document;
    }

    // setData from parent components ie: ui-stepper
    setData(data) {
        if(this.document) this.document.setData(data);
    }
    // setData from parent components ie: ui-stepper
    reload() {
        if(this.document) this.document.setData(data);
    }

    render() {
        return html`
            ${this.renderComponent()}
        `;
    }
}
customElements.define("ui-document", Document)
