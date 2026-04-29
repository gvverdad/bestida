import { LitElement, html, css, nothing } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../css/tw.js'

import "../../icons/x.js"
import { isNull, isEmpty, isNil } from "../utils"

class Input extends LitElement {
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
        type: { type: String },
        fieldType: { attribute: "field-type", type: String },
        name: { type: String },
        placeHolder: { attribute: "placeholder", type: String },
        value: { type: String },
        rows: { attribute: "text-rows", type: Number },

        integerMessage: { attribute: "integer-message", type: String },
        positiveMessage: { attribute: "positive-message", type: String },
        zeropositiveMessage: { attribute: "zero-positive-message", type: String },
        negativeMessage: { attribute: "negative-message", type: String },
        zeronegativeMessage: { attribute: "zeronegative-message", type: String },
        notzeroMessage: { attribute: "notzero-message", type: String },
        totalMessage: { attribute: "total-message", type: String },
        minMessage: { attribute: "min-message", type: String },
        maxMessage: { attribute: "max-message", type: String },
        emailMessage: { attribute: "email-message", type: String },

        labelClass: { attribute: "label-class", type: String },
        inputClass: { attribute: "input-class", type: String },
        fileClass: { attribute: "file-class", type: String },
        textClass: { attribute: "text-class", type: String },

        fileReaderOnLoadHandler: { type: Function },

        readOnly: { type: Boolean },
        disabled: { type: Boolean },
        required: { type: Boolean },
        autoFocus: { attribute: "autofocus", type: Boolean },
        autoComplete: { attribute: "autocomplete", type: Boolean },

        multiple: { type: Boolean },  // comma separated list - 1 input field
        range: { type: Boolean },     // From/To Range - 2 input fields - output is comma separated list of 2 elements

        pattern: { type: String },
        title: { type: String },

        maxLength: { attribute: "maxlength", type: Number },
        minLength: { attribute: "minlength", type: Number },
        min: { type: Number },
        max: { type: Number },
        size: { type: Number },
        step: { type: String },
        height: { type: String },
        width: { type: String },
        list: { type: String },
        accept: { type: String },  // input type file - accepts file types

        validators: { type: Array },
        validator_fields: { attribute: "validator-fields", type: Array },
        validator_messages: { attribute: "validator-messages", type: Array },

        hint: { type: String },

        errorMessage: { state: true }, // error message property from parent form
    };

    constructor() {
        super();
        // bind the event listener to reference the component instance
        this.onInput = this.onInput.bind(this);
        this.onBlur = this.onBlur.bind(this);
        this.onClear = this.onClear.bind(this);

        // defaults
        this.ownerId = null;
        this.owner = null;
        this.label = null;
        this.type = "text";
        this.fieldType = null;
        this.placeHolder = " ";
        this.labelClass = "label block text-sm font-medium leading-6";
        //this.inputClass = "input input-bordered w-full max-w-2xl focus:outline-none focus:border-primary invalid:[&:not(:placeholder-shown):not(:focus)]:border-error peer";
        this.inputClass = "input input-bordered w-full max-w-2xl focus:outline-none focus:border-primary";
        this.textClass = "textarea textarea-bordered textarea-md w-full max-w-2xl focus:outline-none focus:border-primary";
        this.fileClass = "file-input file-input-bordered w-full max-w-2xl focus:outline-none focus:border-primary";

        this.rows = 5;

        this.readOnly = false;
        this.disabled = false;
        this.required = false;
        this.autoFocus = false;
        this.origAutoFocus = false;
        this.autoComplete = false;
        this.multiple = false;
        this.range = false;
        this.multiline = false;

        this.isRegistered = false;

        this.fileReaderOnLoadHandler = null;

        this.value = null;
        this.fromValue = "";
        this.toValue = "";
        this.pattern = "";
        this.title = "";
        this.maxLength = "";
        this.min = "";
        this.max = "";
        this.size = "";
        this.step = "";
        this.height = "";
        this.width = "";
        this.list = "";
        this.accept = null;

        this.errorMessage = "";

        this.validators = null;
        this.validator_fields = null;
        this.validator_messages = null;

        this.hint = null;
    }

    connectedCallback() {
        super.connectedCallback();

        if(this.range && this.value) {
            // remove quotes in string if ever
            const parts = this.value.trim().replace(/^"|"$/g, '').split(',');
            this.fromValue = (parts[0] || '').trim();
            this.toValue = (parts[1] || '').trim();
        }

        if(isNull(this.fieldType)) {
            switch(this.type) {
                case "password":
                    this.fieldType = "String";
                    break;
                case "email":
                    this.fieldType = "String";
                    break;
                case "checkbox":
                    this.fieldType = "Boolean";
                    break;
                case "number":
                    this.fieldType = "Numeric";
                    break;
                case "file":
                    this.fieldType = "File";
                    break;
                default:
                    this.fieldType = "String";
            }
        }

        if(this.type === "file") this.inputClass = this.fileClass;

        this.multiline = this.fieldType === "Text";
        this.origAutoFocus = this.autoFocus;
    }

    onInput(event) {
        if(this.type === "number") {
            // TODO: firefox -10  (-ve numbers)
            // works by entering 10 then inserting the -ve sign
            if(event.target.value === "") {
                // value is empty if value entered isNaN
                event.target.value = "";  // Clears the input field
                //return false;
            } else if(event.target.value && isNaN(event.target.value)) {
                // value entered isNaN
                event.target.value = ""; // Clears the input field
                //return false;
            }
            // allow to drop thru to update this.value and
            // be validated - notZero, positive, etc
        }

        if(this.type === "file") this.handleInput(event.target.files[0], event.target.id);
        else this.handleInput(event.target.value, event.target.id);
    }

    async handleInput(value, target=null) {
        if(this.type === "file") {
            const file = value;
            // TODO: check why isEmpty(file).isObject() is not detecting Object.keys
            // use isNil instead of isEmpty
            if(isNil(file)) return false;

            const data = new FormData();
            data.append("file", file);
            try {
                value = await api.POST("/upload", data, "file");
                //value = JSON.stringify(value);

                if(this.fileReaderOnLoadHandler) {
                    const reader = new FileReader();
                    reader.onload = this.fileReaderOnLoadHandler;
                    reader.readAsArrayBuffer(file);
                    /***
                        reader.readAsArrayBuffer() is not limited to specific file types.
                        It can be used for any file, and the ArrayBuffer it returns can be
                        processed further depending on the file's format.
                    ***/
                }
            } catch (err) {
                value = "";
                console.log("input.handleInput error:", err);
                const message = `input.handleInput ${err.status}  ${err.detail}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        }

        if(this.range &&
            !isNil(target) &&
            (target.startsWith("From.") || target.startsWith("To."))) {
            if(target.startsWith("From.")) this.fromValue = value;
            else this.toValue = value;
            // update this.value in onBlur - this.value is a reactive property
        } else {
            if(this.type === "number") this.value = Number(value);
            else this.value = value;
        }

        // bubble up event to parent Lit form
        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: { key: this.name,
                              value: this.value,
                              type: this.type,
                              fieldType: this.fieldType,
                              field: this,
                              record: null,
                              sender: ["Input.handleInput"]
                              }
        }));
    }

    onBlur(event) {
        if(this.range && !this.multiline) {
            // update this.value here instead in onHandleInput - this.value is reactive
            // and will call render and disrupt the flow of input From to To
            this.value = `${this.fromValue},${this.toValue}`;
            // bubble up event to parent Lit form
            this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: { key: this.name,
                              value: this.value,
                              type: this.type,
                              fieldType: this.fieldType,
                              field: this,
                              record: null,
                              sender: ["Input.handleInput"]
                              }
            }));
        }
        // bubble up event to parent Lit form
        this.dispatchEvent(new CustomEvent(`form-field-blur-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: { key: this.name }
        }));
    }

    onClear(event) {
        this.handleInput("");
        // dont know why but input is not cleared
        const input = this.shadowRoot.getElementById(this.name);
        input.value = "";
    }

    setFieldValue(value) {
        this.handleInput(value);
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

        let name = this.name;
        if(this.range) name = `From.${this.name}`;

        if(error_box) {
            if(this.errorMessage) {
                error_box.textContent = this.errorMessage;
                error_box.classList.remove("hidden");
                this.shadowRoot.getElementById(name).classList.add("border-error");
            } else {
                error_box.textContent = "";
                error_box.classList.add("hidden");
                this.shadowRoot.getElementById(name).classList.remove("border-error");
            }
        }
        // this.autoFocus is turned off/on by form validation
        if(this.autoFocus) {
            const ele = this.shadowRoot.getElementById(name);
            ele.focus();
            // position cursor on the last char + 1
            // setSelectionRange only works with input type: text, textarea
            try { ele.setSelectionRange(ele.value.length, ele.value.length); }
            catch {}
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
        if(hide && !isNil(this.shadowRoot)) {
            const error_box = this.shadowRoot.querySelector("[data-error]");
            if(error_box) {
                this.errorMessage = "";
                error_box.classList.add("hidden");
            }
        }

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
        const display = this.type === "hidden" ? "display: none" : "display: block";
        // To refer to hyphenated properties such as font-family,
        // use the camelCase equivalent (fontFamily) or
        // place the hyphenated property name in quotes ('font-family').
        const rightClasses = {
            "right-0": this.type === "number" ? false : true,
            "right-10": this.type === "number" ? true : false,  // allow for spinner
        };

        return html`
            <div class="form-control" style="${display}">
            ${this.type !== "hidden" && this.label
            ?   html`
                    <label class="${this.labelClass}" for="${this.name}">
                        <span class="label-text">${this.label}</span>
                    </label>`
            :   nothing
            }
            ${this.multiline
            ?   html`
                    <textarea
                        name="${this.name}"
                        id="${this.name}"

                        ${!isEmpty(this.placeHolder)
                        ?   html `
                                placeholder="${this.placeHolder}"
                            `
                        :   nothing
                        }
                        class="${this.textClass || nothing}"

                        rows="${this.rows}"

                        ?readonly="${this.readOnly}"
                        ?disabled="${this.disabled}"
                        ?required="${this.required}"
                        ?autofocus="${this.autoFocus}"
                        maxlength="${this.maxLength || nothing}"

                        @input="${this.onInput}"
                        @click="${this.onInput}"
                        @blur="${this.onBlur}"
                    >${this.value || nothing}</textarea>`
            :  this.range && this.type !== "hidden"
            ?  html`
                <div class="form-control grid grid-cols-2 gap-2">
                    <input
                        type="${this.type}"
                        name="${`From.${this.name}`}"
                        id="${`From.${this.name}`}"
                        placeholder="From"
                        class="${this.inputClass || nothing}"
                        value="${this.fromValue || nothing }"

                        pattern="${this.pattern || nothing}"
                        title="${this.title || nothing}"
                        maxlength="${this.maxLength || nothing}"
                        minlength="${this.minLength || nothing}"
                        min="${this.min || nothing}"
                        max="${this.max || nothing}"
                        size="${this.size || nothing}"
                        step="${this.step || nothing}"
                        height="${this.height || nothing}"
                        width="${this.width || nothing}"
                        list="${this.list || nothing}"

                        accept="${this.accept || nothing}"

                        ?readonly="${this.readOnly}"
                        ?disabled="${this.disabled}"
                        ?required="${this.required}"
                        ?autofocus="${this.autoFocus}"
                        ?autocomplete="${this.autoComplete}"

                        @input="${this.onInput}"
                        @blur="${this.onBlur}"
                    />
                    <input
                        type="${this.type}"
                        name="${`To.${this.name}`}"
                        id="${`To.${this.name}`}"
                        placeholder="To"
                        class="${this.inputClass || nothing}"
                        value="${this.toValue || nothing }"

                        pattern="${this.pattern || nothing}"
                        title="${this.title || nothing}"
                        maxlength="${this.maxLength || nothing}"
                        minlength="${this.minLength || nothing}"
                        min="${this.min || nothing}"
                        max="${this.max || nothing}"
                        size="${this.size || nothing}"
                        step="${this.step || nothing}"
                        height="${this.height || nothing}"
                        width="${this.width || nothing}"
                        list="${this.list || nothing}"

                        accept="${this.accept || nothing}"

                        ?readonly="${this.readOnly}"
                        ?disabled="${this.disabled}"
                        ?required="${this.required}"
                        ?autofocus="${this.autoFocus}"
                        ?autocomplete="${this.autoComplete}"

                        @input="${this.onInput}"
                        @blur="${this.onBlur}"
                    />
                    ${!isEmpty(this.hint)
                    ? html`<p class="col-span-2 label-text-alt">${this.hint}</p>`
                    : nothing}
                    <p data-error="${this.name}"
                        class="col-span-2 hidden block mt-2 text-sm text-red-500 peer-[&:not(:placeholder-shown):not(:focus):invalid]:block">
                    </p>
                </div>`
            :  html`
                <div class="form-control w-full flex items-center relative max-w-2xl"
                    style="${display}"
                >
                    <input type="${this.type}"
                        name="${this.name}"
                        id="${this.name}"

                        ${!isEmpty(this.placeHolder)
                        ?   html `
                                placeholder="${this.placeHolder || nothing}"
                            `
                        :   nothing
                        }

                        class="${this.inputClass || nothing}"

                        value="${this.value || nothing }"
                        pattern="${this.pattern || nothing}"
                        title="${this.title || nothing}"
                        maxlength="${this.maxLength || nothing}"
                        minlength="${this.minLength || nothing}"
                        min="${this.min || nothing}"
                        max="${this.max || nothing}"
                        size="${this.size || nothing}"
                        step="${this.step || nothing}"
                        height="${this.height || nothing}"
                        width="${this.width || nothing}"
                        list="${this.list || nothing}"

                        accept="${this.accept || nothing}"

                        ?readonly="${this.readOnly}"
                        ?disabled="${this.disabled}"
                        ?required="${this.required}"
                        ?autofocus="${this.autoFocus}"
                        ?autocomplete="${this.autoComplete}"
                        ?multiple="${this.multiple}"

                        @input="${this.onInput}"
                        @click="${this.onInput}"
                        @blur="${this.onBlur}"
                    />
                    ${this.type !== "hidden" && !this.required && !this.disabled && !this.readOnly
                        ? html`<button
                            class="${classMap(rightClasses)} absolute inset-y-0 flex items-center px-2"
                            @click="${this.onClear}"
                        >
                            <icon-x></icon-x>
                        </button>`
                    : nothing}
                </div>`
            }
            ${this.type !== "hidden"
            ?   html`
                    ${!isEmpty(this.hint)
                    ? html`<span class="label-text-alt">${this.hint}</span>`
                    : nothing}
                    <span data-error="${this.name}"
                        class="hidden block mt-2 text-sm text-red-500 peer-[&:not(:placeholder-shown):not(:focus):invalid]:block">
                    </span>
                `
            :   nothing
            }
            </div>
        `;
    }
}

customElements.define("ui-input", Input)
