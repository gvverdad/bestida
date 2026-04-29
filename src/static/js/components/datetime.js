import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../css/tw.js'

import flatpickr from "flatpickr";
import 'flatpickr/dist/flatpickr.min.css';
import { parse } from "date-fns";

import "../../icons/calendars.js"
import "../../icons/x.js"
import store from "../store"
import { isNull, isEmpty, isNil, dateTimeFormat, isArray } from "../utils"

class DateTimeField extends LitElement {
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
        type: { type: String },  // input type - text, hidden
        fieldType: { attribute: "field-type", type: String }, // Date, Time, DateTime
        mode: { type: String },  // single/range/multiple
        name: { type: String },
        // value is iso string - see date-fns unicode token for format
        // fieldType Date = yyyy-MM-dd
        // fieldType Time = yyyy-MM-dd'T'HH:mm:ss
        // fieldType DateTime = yyyy-MM-dd'T'HH:mm:ssXXX
        value: { type: String },

        defaultDate: { attribute: "default-date", type: Boolean },  // populate Flatpickr with now
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
        this.onInput = this.onInput.bind(this);
        this.onBlur = this.onBlur.bind(this);
        this.onClear = this.onClear.bind(this);
        this.onCalendar = this.onCalendar.bind(this);
        this.handleFlatpickrChange = this.handleFlatpickrChange.bind(this);

        // default
        this.ownerId = null;
        this.label = null;
        this.name = null;
        this.type = "text";
        this.fieldType = "Date";  // Date,Time,DateTime
        this.mode = "single";     // single/range/multiple
        this.placeHolder = " ";

        this.defaultDate = false;   // populate Flatpickr with now
        this.readOnly = false;
        this.disabled = false;
        this.required = false;
        this.autoFocus = false;
        this.origAutoFocus = false;
        this.multiple = false;

        this.isRegistered = false;

        this.value = null;

        this.dateTimePicker = null;

        this.errorMessage = "";
        this.format = null;

        this.validators = null;
        this.validator_fields = null;
        this.validator_messages = null;
    }

    connectedCallback() {
        super.connectedCallback();

        this.origAutoFocus = this.autoFocus;

        if(isNil(this.mode)) this.mode = "single";
        if(this.mode !== "single") {
            this.defaultDate = false;
        }

        if(this.value) {
            // this.value is iso string - see date-fns unicode token for format
            // date = yyyy-MM-dd
            // time = yyyy-MM-dd'T'HH:mm:ss
            // datetime = yyyy-MM-dd'T'HH:mm:ssXXX
            if(typeof this.value === 'string' && !isEmpty(this.value)) {
                // check if time string is time only (HH:mm:ss)
                if(this.value.includes(":") && !this.value.includes("T") &&
                    !this.value.includes("-")) {
                    const [hours, minutes, seconds] = this.value.split(':').map(Number);
                    this.value = new Date(1970, 0, 1, hours, minutes, seconds);
                } else this.value = new Date(this.value);
            } if(isArray(this.value)) {
                let value = [];
                this.value.forEach(val => {
                    value.push(new Date(val));
                });
                this.value = value;
            }
        }

        this.format = dateTimeFormat(store.get("user.Settings.Locale")[0], this.fieldType);
    }

    getFpFormat() {
        // mapping: date-fns unicode token = Flatpickr formatting token
        const mapping = {
            dd: "d", // Day with leading zero
            d: "j",  // Day without leading zero
            MM: "m", // Month with leading zero
            M: "n",  // Month without leading zero
            yyyy: "Y", // Full year
            yy: "y",  // Two-digit year
            hh: "G",  // Hour with leading zero
            mm: "i",  // minute with leading zero
            ss: "S",  // seconds with leading zero
            a: "K",  // AM/PM
        };

        // Replace each part of the format based on the mapping
        return this.format.replace(/dd|MM|yyyy|d|M|yy|hh|mm|ss|a/g, match => mapping[match]);
    }

    firstUpdated() {
        const input = this.shadowRoot.getElementById(this.name);
        const fpFormat = this.getFpFormat();
        /*
            TODO: sticky position when scrolling/resize
        */
        this.dateTimePicker = flatpickr(input, {
            allowInput: false, // this.mode === "single" ? true : false,
            clickOpens: true, // this.mode === "single" ? false : true,
            conjunction: ",",
            enableTime: this.fieldType === "Date" ? false : true,
            enableSeconds: this.fieldType === "Date" ? false : true,
            noCalendar: this.fieldType === "Time" ? true : false,
            minuteIncrement: 1,
            time_24hr: false,
            dateFormat: fpFormat,
            position: "auto right",
            onChange: this.handleFlatpickrChange,
            locale: {
               firstDayOfWeek: 1  // Monday
            },
            weekNumbers: false,
            mode: this.mode   // single/range/multiple
        });

        // styling the date picker
        const calendarContainer = this.dateTimePicker.calendarContainer;

        calendarContainer.className = `${calendarContainer.className} bg-base-100 p-4 w-fit border border-primary rounded-lg shadow-lg font-sans text-sm font-normal text-blue-gray-500 focus:outline-none break-words whitespace-normal`;
        // the p-4 w-fit override above have no effect - force override flatpicker-calendar padding and width
        calendarContainer.style.padding = "1rem";

        if(this.fieldType !== "Time") {
            calendarContainer.style.width = "fit-content";

            const calendarMonthNav = this.dateTimePicker.monthNav;
            const calendarNextMonthNav = this.dateTimePicker.nextMonthNav;
            const calendarPrevMonthNav = this.dateTimePicker.prevMonthNav;
            const calendarDaysContainer = this.dateTimePicker.daysContainer;

            calendarMonthNav.className = `${calendarMonthNav.className} flex items-center justify-between mb-4 [&>div.flatpickr-month]:-translate-y-3`;
            calendarNextMonthNav.className = `${calendarNextMonthNav.className} absolute !top-2.5 !right-1.5 h-6 w-6 bg-transparent hover:bg-blue-gray-50 !p-1 rounded-md transition-colors duration-300`;
            calendarPrevMonthNav.className = `${calendarPrevMonthNav.className} absolute !top-2.5 !left-1.5 h-6 w-6 bg-transparent hover:bg-blue-gray-50 !p-1 rounded-md transition-colors duration-300`;
            calendarDaysContainer.className = `${calendarDaysContainer.className} [&_span.flatpickr-day]:!rounded-md [&_span.flatpickr-day.selected]:!bg-gray-900 [&_span.flatpickr-day.selected]:!border-gray-900`;
        }

        if(isEmpty(this.value) && this.defaultDate) {
            this.value = new Date();
        }

        if(!isNil(this.value)) {
            this.dateTimePicker.setDate(this.value);
        }
        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: { key: this.name,
                      value: this.value,
                      type: this.type,
                      fieldType: this.fieldType,
                      field: this,
                      record: null,
                      sender: ["DateTimeField.firstUpdated"]
            }
        }));

        // TODO: input mask

        /* advise parent render is complete */
        this.dispatchEvent(new CustomEvent(`render-complete-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: { key: this.name }
        }));
    }

    onCalendar(event) {
        event.stopPropagation();
        // TODO: fix toggle
        if(this.dateTimePicker) {
            // toggle
            if(this.dateTimePicker.isOpen) {
                this.dateTimePicker.close();
            } else {
                this.dateTimePicker.open();
            }
        }
    }

    onClear(event) {
        this.value = null;
        this.dateTimePicker.clear();
    }

    onInput(event) {
        //this.handleInput(event.target.value);
    }

    handleFlatpickrChange(selectedDates, dateStr, instance) {
        if(selectedDates.length) {
            let dates = selectedDates
            if(this.mode === "single") dates = selectedDates[0];
            this.handleInput(dates);
        } else this.handleInput("");
    }

    handleInput(value) {
        if(isArray(value)) this.value = value;
        else if(value instanceof Date) this.value = value;
        else if(!isEmpty(value) && typeof value === 'string') {
            // string convert to date
            const format = dateTimeFormat(store.get("user.Settings.Locale")[0], this.fieldType);
            try {
                this.value = parse(value, format, new Date());
            } catch { return false; }
        } else this.value = null;
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
                              sender: ["DateTimeField.handleInput"]
                              }
        }));
    }

    onBlur(event) {
        // bubble up event to parent Lit form
        this.dispatchEvent(new CustomEvent(`form-field-blur-${this.ownerId}`, {
                    bubbles: true,
                    composed: true,
                    detail: { key: this.name }
        }));
    }

    setFieldValue(value) {
        // value should be a date object or iso date string or null
        if(value instanceof Date) this.value = value;
        else if(!isEmpty(value) && typeof value === 'string') this.value = new Date(value);
        else this.value = null;

        if(this.dateTimePicker) {
            this.dateTimePicker.setDate(this.value);
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
                              sender: ["DateTimeField.setFieldValue"]
                              }
        }));
    }

    updated() {
        // apply properties from Lit Form
        const error_box = this.shadowRoot.querySelector("[data-error]");
        if(error_box) {
            if(this.errorMessage) {
                error_box.textContent = this.errorMessage;
                error_box.classList.remove("hidden");
                this.shadowRoot.getElementById(this.name).classList.add("border-error");
            } else {
                error_box.textContent = "";
                error_box.classList.add("hidden");
                this.shadowRoot.getElementById(this.name).classList.remove("border-error");
            }
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

        return html`
            <div class="form-control" style="${display}">
            ${this.type !== "hidden" && this.label
            ?   html`
                    <label class="label block text-sm font-medium leading-6" for="${this.name}">
                        <span class="label-text">${this.label}</span>
                    </label>`
            :   nothing
            }
            <div class="form-control w-full flex items-center relative max-w-2xl"
                style="${display}"
            >
                <input type="${this.type}"
                    name="${this.name}"
                    id="${this.name}"

                    class="input input-bordered w-full focus:outline-none focus:border-primary pr-12"

                    value="${this.value || nothing}"
                    placeholder="${this.format.toLowerCase()}"

                    ?readonly="${this.readOnly}"
                    ?disabled="${this.disabled}"
                    ?required="${this.required}"
                    ?autofocus="${this.autoFocus}"

                    @input="${this.onInput}"

                    @blur="${this.onBlur}"
                />
                ${this.type !== "hidden" && !this.required && !this.disabled && !this.readOnly
                    ? html`<button
                        class="absolute inset-y-0 right-10 flex items-center px-2"
                        @click="${this.onClear}"
                    >
                        <icon-x></icon-x>
                    </button>`
                : nothing}
                ${this.type !== "hidden"
                    ? html`<button
                        class="absolute inset-y-0 right-0 flex items-center px-2"
                        @click="${this.onCalendar}"
                    >
                        <icon-calendars></icon-calendars>
                    </button>`
                : nothing}
            </div>
            ${this.type !== "hidden"
            ?   html`
                    <span data-error="${this.name}"
                        class="hidden block mt-2 text-sm text-red-500 peer-[&:not(:placeholder-shown):not(:focus):invalid]:block">
                    </span>`
            :   nothing
            }
            </div>
        `;
    }
}

customElements.define("ui-datetime", DateTimeField)
