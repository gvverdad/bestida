import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../css/tw.js'

import { isEmpty, isNil } from "../utils"

class Checkbox extends LitElement {
    static styles = [
        css `
            :host{
                display: block;
            }
        `,
        TWStyles
    ];

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        owner: { type: Object },
        label: { type: String },
        name: { type: String },
        value: { type: String },

        readOnly: { type: Boolean },
        disabled: { type: Boolean },
        required: { type: Boolean },
        autoFocus: { attribute: "autofocus", type: Boolean },

        validators: { type: Array },
        validator_fields: { attribute: "validator-fields", type: Array },
        validator_messages: { attribute: "validator-messages", type: Array },

        errorMessage: { state: true }, // error message property from parent form
    };

    constructor() {
        super();
        // bind the event listener to reference the component instance
        this.handleInput = this.handleInput.bind(this);
        this.handleBlur = this.handleBlur.bind(this);

        // defaults
        this.ownerId = null;
        this.owner = null;
        this.label = null;

        this.readOnly = false;
        this.disabled = false;
        this.required = false;
        this.autoFocus = false;
        this.origAutoFocus = false;

        this.isRegistered = false;

        this.value = false;
        this.errorMessage = "";
        this.fieldType = "Boolean";

        this.validators = null;
        this.validator_fields = null;
        this.validator_messages = null;
    }

    connectedCallback() {
        super.connectedCallback();

        this.origAutoFocus = this.autoFocus;
    }

    handleInput(event) {
        // bubble up event to parent Lit form
        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: { key: this.name,
                              value: event.target.checked,
                              type: this.fieldType,
                              fieldType: this.fieldType,
                              field: this,
                              record: null,
                              sender: ["Checkbox.handleInput"]
                              }
        }));
    }

    handleBlur(event) {
        // bubble up event to parent Lit form
        this.dispatchEvent(new CustomEvent(`form-field-blur-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: { key: this.name }
        }));
    }

    setFieldValue(value) {
        this.value = value;
    }

    firstUpdated() {
        /* advise parent render is complete */
        this.dispatchEvent(new CustomEvent(`render-complete-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: { key: this.name }
        }));
    }

    updated() {
        // apply properties from Lit Form
        const error_box = this.shadowRoot.querySelector("[data-error]");
        if(this.errorMessage) {
            error_box.textContent = this.errorMessage;
            error_box.classList.remove("hidden");
            this.shadowRoot.getElementById(this.name).classList.add("border-error");
        } else {
            error_box.textContent = "";
            error_box.classList.add("hidden");
            this.shadowRoot.getElementById(this.name).classList.remove("border-error");
        }
        // this.autoFocus is turned off/on by form validation
        if(this.autoFocus) {
            this.shadowRoot.getElementById(this.name).focus();
        }
        if(!this.isRegistered && !isEmpty(this.ownerId)) {
            this.isRegistered = true;

            this.dispatchEvent(new CustomEvent(`form-field-register-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: { key: this.name,
                          type: this.fieldType
                        }
            }));
        }
    }

    hide(hide=true) {
        this.style.display = hide ? "none" : "block";
    }

    // called by form to refocus
    focus() {
        if(this.origAutoFocus) this.autoFocus = true;
    }

    shouldUpdate(changedProperties) {
        // check if can render
        if(isNil(this.ownerId)) return false;
        else return true;
    }

    reload() {
        // called by owner - form
    }

    render() {
        return html`
            <div class="flex flex-row flex-wrap">
                <label class="cursor-pointer label font-medium text-sm">
                    <input type="checkbox" id="${this.name}" name="${this.name}"
                        @input="${this.handleInput}"
                        @blur="${this.handleBlur}"
                        ?checked="${this.value === true}"
                        ?readonly="${this.readOnly}"
                        ?disabled="${this.disabled}"
                        ?required="${this.required}"
                        ?autofocus="${this.autoFocus}"
                        class="toggle toggle-sm toggle-primary me-1 focus:outline-none focus:border-primary"/>
                    ${this.label ?
                        html`
                            <span class="label-text">${this.label}</span>`
                    :   nothing}
                </label>
            </div>
            <span data-error="${this.name}"
                class="hidden block mt-2 text-sm text-red-500 peer-[&:not(:placeholder-shown):not(:focus):invalid]:block">
            </span>
        `;
    }
}

customElements.define("ui-checkbox", Checkbox)
