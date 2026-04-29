import { LitElement, html, css, nothing } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { ifDefined } from 'lit/directives/if-defined.js';
import { TWStyles } from '../../css/tw.js'

import api from "../api"
import store from "../store"
import "../../icons/x.js"
import { get, isArray, isObject, isNull, isNil, isEmpty } from "../utils"

class Combobox extends LitElement {
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
        placeHolder: { attribute: "placeholder", type: String },
        value: { type: String },

        formData: { attribute: "form-data", type: Object},
        parentRow: { attribute: "parent-row", type: Object },

        autoDefault: { type: Boolean },  // auto default to first entry
        readOnly: { type: Boolean },
        disabled: { type: Boolean },
        required: { type: Boolean },
        autoFocus: { attribute: "autofocus", type: Boolean },
        autoComplete: { attribute: "autocomplete", type: Boolean },
        multiple: { type: Boolean },

        maxItems: { type: Number },     // maximum drop down items - defaults to 10

        // Select options
        selectTable: { type: String },  // Tablename - used for server update
        selectObject: { type: String },  // Tablename - used for client selection list
        joinList: { type: Array },
        selectId: { type: String },     // FieldName of Tablename Primary Key
        selectKey: { type: String },    // FieldName of Tablename Description to search
        selectColumn: { type: String },  // Datatable selection criteria Column name (non join field)
        selectFormat: { type: Array }, // List of FieldNames for dropdown Display
        selectCascade: { type: Array }, // Array of {field: FieldName, value:}
        // Additional Filter
        validValues: { type: Array }, // Array of valid values
        validValuesKey: { type: String }, // Fieldname for validValues else selectKey
        selectField: { type: String }, // FieldName
        selectFieldValue: { type: String }, // Value FieldName
        selectTableFieldValue: { type: Array },  // Array of {field: FieldName, value:}
        selectGetter: { type: String },  // getter url instead of /list

        // Enum options
        choicesGetter: { attribute: "enum-getter", type: String },
        choices: { type: Object },  // Enum json object (tuple of 2), instead of selectTable

        fieldType: { attribute: "field-type", type: String },  // Enum or Select

        debounceDelay: { attribute: "debounce-delay", type: Number },  // delay in ms
        debounceChars: { attribute: "debounce-chars", type: Number },  // number of chars

        validators: { type: Array },
        validator_fields: { attribute: "validator-fields", type: Array },
        validator_messages: { attribute: "validator-messages", type: Array },

        selectedItems: { state: true },
        inputTagId: { state: true },
        inputDivTagId: { state: true },
        selectTagId: { state: true },
        dropdownTagId: { state: true },
        keyword: { state: true },           // search Keyword

        errorMessage: { state: true },      // error message property from parent form
    };

    constructor() {
        super();
        // bind the event listener to reference the component instance
        this.handleInput = this.handleInput.bind(this);
        this.onBlur = this.onBlur.bind(this);
        this.onOptionClick = this.onOptionClick.bind(this);
        this.onOptionScroll = this.onOptionScroll.bind(this);
        this.onInput = this.onInput.bind(this);
        this.onClick = this.onClick.bind(this);
        this.onClear = this.onClear.bind(this);
        this.onInputFocus = this.onInputFocus.bind(this);
        this.onRemoveSelection = this.onRemoveSelection.bind(this);

        this.debounceDelay = 300;  // delay in ms
        this.debounceChars = 2;    // number of input chars
        this.debounceTimeout = null;

        this.ownerId = null;
        this.owner = null;
        this.label = null;
        this.placeHolder = "";
        this.selectTable = null;
        this.selectObject = null;
        this.joinList = null;
        this.selectId = null;
        this.selectKey = null;
        this.selectColumn = null;
        this.selectFormat = null;
        this.validValues = null;
        this.validValuesKey = null;
        this.selectField = null;
        this.selectFieldValue = null;
        this.selectTableFieldValue = null;
        this.selectCascade = null;
        this.selectGetter = null;

        this.multiple = false;
        this.autoDefault = false;
        this.readOnly = false;
        this.disabled = false;
        this.required = false;
        this.autoFocus = false;
        this.origAutoFocus = false;
        this.autoComplete = false;

        this.choices = null;
        this.choicesGetter = null;

        this.fieldType = null;
        this.maxItems = 10;
        this.value = null;
        this.fromValue = "";
        this.toValue = "";
        this.errorMessage = "";
        this.keyword = "";

        this.validators = null;
        this.validator_fields = null;
        this.validator_messages = null;

        this.isRegistered = false;

        this.formData = null;
        this.parentRow = null;

        this.currentPage = 0;
        this.totalItems = 0;
        this.selectedItems = [];
    }

    connectedCallback() {
        super.connectedCallback();

        this.inputTagId = `${this.name}-input`;
        this.inputDivTagId = `${this.name}-inputDiv`;
        this.selectTagId = `${this.name}-select`;
        this.dropdownTagId = `${this.name}-dropdown`;
        this.origAutoFocus = this.autoFocus;

        if(isNull(this.fieldType)) {
            if(this.choices || this.choicesGetter)  this.fieldType = "Enum";
            else this.fieldType = "Select";
        }

        if(!isNull(this.value)) {
            try {
                this.value = JSON.parse(this.value);
                if(this.multiple) {
                    if(isEmpty(this.value)) {
                        this.value = [];
                    } else if(!isArray(this.value)) {
                        this.value = this.value.split(",");
                    }
                } else {
                    if(isArray(this.value)) this.keyword = this.value[1];
                    else if(isObject(this.value)) this.keyword = get(this.value, this.selectKey);
                    else this.keyword = this.value;
                }
            } catch (error) {
                this.keyword = this.value;
            }
        } else if(this.multiple) {
            this.value = [];
        }
    }

    async firstUpdated() {
        const combobox_input = this.shadowRoot.getElementById(this.inputTagId);
        const combobox_select = this.shadowRoot.getElementById(this.selectTagId);

        // populate select options
        let isSelected = false;
        if(this.fieldType === "Enum") {
            if(this.choices) {
                this.totalItems = this.choices.length;
                this.choices.forEach(item => {
                    if(!isEmpty(this.validValues) && !this.validValues.includes(item[0])) return;

                    const option = document.createElement("option");
                    option.value = item[0];
                    option.textContent = JSON.stringify(item);
                    if(this.multiple && !isEmpty(this.value)) {
                        if(!isArray(this.value)) this.value = this.value.split(",");
                        this.value.forEach(ele => {
                            if(item[0] === ele) {
                                option.selected = true;
                                isSelected = true;
                                this.selectedItems.push({
                                    "key": item[0],
                                    "text": item[1],
                                    "record": item
                                });
                            }
                        });
                    } else if(!isEmpty(this.keyword) &&
                        (this.keyword === this.value && this.keyword === item[0]) ||
                        (this.keyword !== this.value && this.keyword === item[1])) {
                            option.selected = true;
                            isSelected = true;
                            combobox_input.value = item[1];
                    }
                    // append automatically selects first option
                    combobox_select.append(option);
                });
            } else {
                try {
                    await api.GET(`/${this.choicesGetter}`, null, "json")
                        .then( data => {
                            this.totalItems = data.recordsTotal;
                            data.data.forEach(item => {
                                if(!isEmpty(this.validValues) && !this.validValues.includes(item[0])) return;

                                const option = document.createElement("option");
                                option.value = item[0];
                                option.textContent = JSON.stringify(item);
                                if(this.multiple && !isEmpty(this.value)) {
                                    this.value.forEach(ele => {
                                        if(item[0] === ele) {
                                            option.selected = true;
                                            isSelected = true;
                                            this.selectedItems.push({
                                                "key": item[0],
                                                "text": item[1],
                                                "record": item
                                            });
                                        }
                                    });
                                } else if(!isEmpty(this.keyword) &&
                                   (this.keyword === this.value && this.keyword === item[0]) ||
                                   (this.keyword !== this.value && this.keyword === item[1])) {
                                    option.selected = true;
                                    isSelected = true;
                                    combobox_input.value = item[1];
                                }
                                // append automatically selects first option
                                combobox_select.append(option);
                            });
                        });
                } catch (err) {
                    console.log("combobox.firstUpdated1 error:", err);
                    const message = `combobox.firstUpdated1 ${err.status} ${err.detail} : ${this.choicesGetter}`;
                    const toaster = document.querySelector("[data-toaster]");
                    toaster.show(message,"error");
                }
            }
        } else {
            try {
                await this.getOptions(this.keyword, this.currentPage)
                    .then((data) => {
                        this.totalItems = data.recordsTotal;
                        data.data.forEach(record => {
                            const option = document.createElement("option");
                            option.value = get(record, this.selectId, "");
                            option.textContent = JSON.stringify(record);
                            const desc = get(record, this.selectKey);

                            if(this.multiple) {
                                const recId = get(record, this.selectId);
                                this.value.forEach(item => {
                                    const key = get(item, this.selectId);
                                    if(key === recId) {
                                        option.selected = true;
                                        isSelected = true;
                                        this.selectedItems.push({
                                            "key": option.value,
                                            "text": desc,
                                            "record": record
                                        });
                                    }
                                });
                            } else if(!isEmpty(this.keyword) &&
                                this.keyword === desc) {
                                option.selected = true;
                                isSelected = true;
                                combobox_input.value = desc;
                            }
                            // append automatically selects first option
                            combobox_select.append(option);
                        });
                    });
            } catch (err) {
                console.log("combobox.firstUpdated2 error:", err);
                const message = `combobox.firstUpdated2 ${err.status} ${err.detail} : ${this.name}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");
            }
        }
        if(!this.autoDefault && !isSelected) {
            // force no selection
            combobox_select.selectedIndex = -1;
        }

        // apply default selected option
        if(!isNull(this.value) && !this.multiple) {
            if(isObject(this.value)) {
                if(isArray(this.value)) combobox_select.value = this.value[0];
                else combobox_select.value = get(this.value, this.selectId, "");
            } /* else if(isEmpty(this.value)) {
                const option = document.createElement("option");
                option.value = "";
                if(this.fieldType === "Enum") option.textContent = JSON.stringify(["",""]);
                else option.textContent = JSON.stringify({});
                combobox_select.append(option);
                combobox_select.value = this.value;
            } */
        }
        // advise parent of selected option
        if(!this.multiple && combobox_select.options.length &&
            !isEmpty(combobox_select.value)) {
            let record = JSON.parse(combobox_select.selectedOptions[0].text);

            if(!isObject(this.value)) this.value = record;
            let field_value = record;
            if(this.fieldType === "Enum") {
                combobox_input.value = record[1];
                field_value = record[0];
            } else {
                combobox_input.value = get(record, this.selectKey);
                if(this.selectKey.split(".").length > 1) {
                    field_value = get(record, this.name);
                }
            }
            this.value = field_value;
            // init values from select field
            this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: { key: this.name,
                          value: field_value,
                          type: this.fieldType,
                          field: this,
                          record: record,
                          sender: ["Combobox.firstUpdated1"]
                        }
            }));
        } else if(this.multiple) {
            const field_value = [];
            this.selectedItems.forEach(item => {
                if(this.fieldType === "Enum") field_value.push(item.record[0]);
                else field_value.push(item.record);
            });
            this.value = field_value;
            this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: { key: this.name,
                          value: field_value,
                          field: this,
                          type: this.fieldType,
                          sender: ["Combobox.firstUpdated2"]
                        }
            }));
        }
        /* advise parent render is complete */
        this.dispatchEvent(new CustomEvent(`render-complete-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: { key: this.name }
        }));

        if(this.multiple) this.requestUpdate();  // force render
    }

    getOptions(search_key, start=0) {
        const field_list = [];
        if(this.selectId) field_list.push(this.selectId);
        if(this.selectKey) field_list.push(this.selectKey);
        if(this.selectColumn) field_list.push(this.selectColumn);
        if(this.selectFormat) {
            /* Include record Id */
            this.selectFormat.forEach(ele => {
                if(ele.includes(".")) {
                    const idx = ele.lastIndexOf(".");
                    const id = ele.slice(0,idx+1) + "Id";
                    field_list.push(id);
                }
                if(!field_list.includes(ele)) {
                    field_list.push(ele);
                }
            });
            if(!field_list.includes("Id")) {
                field_list.push("Id");
            }
        }

        let select_field_value = null;
        if(!isEmpty(this.selectFieldValue)) {
            // check current record
            select_field_value = get(this.formData, this.selectFieldValue, null);
            if(isNull(select_field_value) && !isNull(this.parentRow)) {
                // check parent row
                select_field_value = get(this.parentRow, this.selectFieldValue, null);
            }
        }

        const crit = [];
        if(this.selectField && !isEmpty(this.selectFieldValue)) {
            // op: 0 = EQUALS
            if(isArray(select_field_value))
                crit.push({"field": this.selectField, "op": 0,
                            "value": select_field_value[0] });
            else
                crit.push({"field": this.selectField, "op": 0,
                            "value": select_field_value });
        }
        if(this.selectTableFieldValue) {
            // op: 0 = EQUALS
            this.selectTableFieldValue.forEach(ele => {
                crit.push({"field": ele.field, "op": 0, "value": ele.value });
            });
        }
        if(!isEmpty(this.validValues)) {
            // op: 8 = IN LIST
            crit.push({"field": this.validValuesKey || this.selectKey,
                        "op": 8, "value": this.validValues });
        }
        if(search_key) {
            // op: 14 = CONTAINS
            crit.push({"field": this.selectKey, "op": 14, "value": search_key });
        }

        const data = {
            "Depth": 1,
            "CompanyRowId": store.get("user.Company_Id"),
            "Locale": store.get("user.Settings.Locale")[0],
            "Timezone": store.get("user.Settings.Timezone")[0],
            "FieldList": field_list,
            "DbTableName": this.selectObject || this.selectTable || this.joinList[0][2],
            "Criteria": crit,
            "CriteriaType": 0, // ALL = 0;ANY = 1;NONE = 2;NOT_ALL = 3
            "Offset": start,
            "PageSize": this.maxItems,
            "TextAsString": true
        }
        const combobox_select = this.shadowRoot.getElementById(this.selectTagId);
        combobox_select.innerHTML = "";

        let url = "/list";
        if(this.selectGetter) url = this.selectGetter;

        return api.POST(url, data, "json");
    }

    fetchOptions(search_key, start=0) {
        const combobox_select = this.shadowRoot.getElementById(this.selectTagId);
        const combobox_dropdown = this.shadowRoot.getElementById(this.dropdownTagId);

        return new Promise(async (resolve) => {
            let isOK = false;
            try {
                await this.getOptions(search_key, start)
                    .then((data) => {
                        this.totalItems = data.recordsTotal;
                        data.data.forEach(record => {
                            const val = get(record, this.selectId, "");
                            const option = document.createElement("option");
                            option.value = val;
                            option.textContent = JSON.stringify(record);
                            combobox_select.append(option);

                            const listItem = document.createElement("li");
                            const listContent = document.createElement("div");

                            const content = get(record, this.selectKey);
                            if(this.value) {
                                if(this.multiple && isArray(this.value)) {
                                    if(this.value.some(opt => get(opt, this.selectKey) === content)) {
                                        listContent.classList.add("active", "menu-item");
                                    }
                                } else {
                                    if(get(this.value, this.selectKey) === content) {
                                        listContent.classList.add("active", "menu-item");
                                    }
                                }
                            }
                            listContent.dataset.combobox_list_element = "true";
                            listContent.dataset.value = val;
                            listContent.dataset.record = JSON.stringify(record);

                            if(this.selectFormat) {
                                let line = '<div class="flex items-center gap-4">';
                                this.selectFormat.forEach(ele => {
                                    line += `<div>${get(record, ele, "")}</div>`;
                                });
                                line += "</div>";
                                listContent.innerHTML = line;
                            } else listContent.textContent = content;

                            listItem.appendChild(listContent);
                            combobox_dropdown.appendChild(listItem);

                            isOK = true;
                        });
                        resolve(isOK);
                    });
            } catch (err) {
                console.log("combobox.fetchOptions error:", err);
                const message = `combobox.fetchOptions ${err.status} ${err.detail} : ${this.name}`;
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(message,"error");

                resolve(false);
            }
        });
    }

    clearDropdown(hide=true) {
        const combobox_dropdown = this.shadowRoot.getElementById(this.dropdownTagId);
        combobox_dropdown.innerHTML = "";
        if(hide) {
            combobox_dropdown.classList.add("hidden");
            this.currentPage = 0;
        }
    }

    onOptionClick(event) {
        // this is a bubbled event - we are interested in the li div[data-combobox_list_element] click
        if(event.target === event.currentTarget) return false;
        if(event.target.tagName.toLowerCase() !== "div") return false;

        let node = event.target;
        if(node.dataset.combobox_list_element === undefined) {
            node = event.target.closest('div[data-combobox_list_element]');
        }
        const value = node.dataset.value;
        let record = null;
        if(this.fieldType === "Enum") {
            record = JSON.parse(node.dataset.record);
            // TODO: dont know why need to run JSON.parse twice on
            // node.dataset.record = "[\"en-ca\",\"English (Canada)\"]"
            if(!isArray(record)) record = JSON.parse(record);
        } else record = JSON.parse(node.dataset.record);

        const combobox_input = this.shadowRoot.getElementById(this.inputTagId);
        const combobox_select = this.shadowRoot.getElementById(this.selectTagId);

        let field_value = record;
        /***********************************************************************
        // toggle selection
        let select = true;
        const optionSelected = combobox_select.querySelector(`option[value="${value}"]`);
        if (optionSelected) {
            // use == instead of === to compare int and string - value is string
            if(this.fieldType === "Enum") {
                if(this.multiple) {
                    const index = this.selectedItems.findIndex(item => item["key"] == value);
                    if(index !== -1) select = false;
                } else {
                    const valu = isArray(this.value) ? this.value[0] : this.value;
                    if(optionSelected.value == valu) select = false;
                }
            } else {
                if(this.value) {
                    if(this.multiple && isArray(this.value)) {
                        if(this.value.some(opt => get(opt, this.selectId) == value)) {
                            select = false;
                        }
                    } else {
                        if(get(this.value, this.selectId) == value) {
                            select = false;
                        }
                    }
                }
            }
            if(!select) {
                optionSelected.selected = false;
                field_value = null;
                this.value = null;
                if(this.multiple) {
                    const index = this.selectedItems.findIndex(item => item["key"] == value);
                    if (index !== -1) {
                        this.selectedItems.splice(index, 1);
                    }
                    field_value = [];
                    this.selectedItems.forEach(item => {
                        if(this.fieldType === "Enum") field_value.push(item.key);
                        else  field_value.push(item.record);
                    });
                    this.value = field_value;
                }
            }
        }
        if(select) {
        ***********************************************************************/
            if(this.multiple) {
                const optionSelected = combobox_select.querySelector(`option[value="${value}"]`);
                if (optionSelected) optionSelected.selected = true;

                if(this.fieldType === "Enum") {
                    this.selectedItems.push({
                        "key": record[0],
                        "text": record[1],
                        "record": record
                    });
                    field_value = [];
                    this.selectedItems.forEach(item => {
                        field_value.push(item.key);
                    });
                } else {
                    this.selectedItems.push({
                        "key": get(record, this.selectId),
                        "text": get(record, this.selectKey),
                        "record": record
                    });
                    field_value = [];
                    this.selectedItems.forEach(item => {
                        field_value.push(item.record);
                    });
                }
                this.value = field_value;
            } else {
                combobox_select.value = value;
                if(this.fieldType === "Enum") {
                    field_value = record[0];
                    combobox_input.value = record[1];
                    this.value = record[1];
                } else {
                    combobox_input.value = get(record, this.selectKey);
                    if(this.selectKey.split(".").length > 1) {
                        field_value = get(record, this.name);
                    }
                    this.value = field_value;
                }
            }
        /** } **/
        // bubble up event to parent Lit form
        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: { key: this.name,
                      value: field_value,
                      type: this.fieldType,
                      field: this,
                      record: record,
                      sender: ["Combobox.onOptionClick"]
                    }
        }));
        this.clearDropdown();

        if(this.multiple) this.requestUpdate();  // force render
    }

    async onOptionScroll(event) {
        event.stopPropagation();
        // scroll event for Select fieldType - virtual scrolling

        const { scrollTop, scrollHeight, clientHeight } = event.target;
        const scrollOffset = 0;  // threshold to trigger fetchOptions

        if ((scrollTop + clientHeight >= scrollHeight - scrollOffset) &&
           ((this.currentPage + 1) * this.maxItems) < this.totalItems) {
            // Scrolled to the bottom: load more options
            this.currentPage += 1;
            await this.fetchOptions(this.keyword, this.currentPage * this.maxItems);
        } else if (scrollTop <= scrollOffset && this.currentPage > 0) {
            // Scrolled to the top: load previous options
            this.currentPage -= 1;
            await this.fetchOptions(this.keyword, this.currentPage * this.maxItems);
        }
    }

    onClick(event) {
        event.stopPropagation();

        if(this.disabled) {
            event.preventDefault();
            return false;
        }
        const combobox_dropdown = this.shadowRoot.getElementById(this.dropdownTagId);
        // toggle
        if(combobox_dropdown.classList.contains("hidden")) {
            this.handleInput("");
        } else {
            this.clearDropdown();
        }
    }

    onInput(event) {
        if(this.disabled) {
            event.preventDefault();
            return false;
        }

        if(event.target.tagName.toLowerCase() !== "input") {
            if(isEmpty(this.keyword)) {
                const combobox_input = this.shadowRoot.getElementById(this.inputTagId);
                this.keyword = combobox_input.value;
            }
            this.handleInput(this.keyword);
            return;
        }

        this.keyword = event.target.value.toLowerCase();

        clearTimeout(this.debounceTimeout);
        if(this.keyword.length % this.debounceChars !== 0) {
            // not multiple of this.debounceChars - wait
            this.debounceTimeout = setTimeout(() => {
                this.handleInput(this.keyword);
            }, this.debounceDelay);
        } else {
            // multiple of this.debounceChars - process
            this.handleInput(this.keyword);
        }
    }

    async handleInput(keyword) {
        this.clearDropdown();

        const combobox_select = this.shadowRoot.getElementById(this.selectTagId);
        const combobox_dropdown = this.shadowRoot.getElementById(this.dropdownTagId);
        const combobox_input = this.shadowRoot.getElementById(this.inputTagId);
        let isOK = false;

        if(this.fieldType === "Enum") {
            let selected = combobox_select.options[combobox_select.selectedIndex];
            if(this.multiple) {
                selected = Array.from(combobox_select.selectedOptions);
            }
            Array.from(combobox_select.options).forEach((option) => {
                const content = JSON.parse(option.textContent)[1];
                if(content.toLowerCase().includes(keyword) || isEmpty(keyword)) {
                    const listItem = document.createElement("li");
                    const listContent = document.createElement("div");
                    if(selected) {
                        if(this.multiple) {
                            if(selected.some(opt => opt.value === option.value)) {
                                listContent.classList.add("active", "menu-item");
                            }
                        } else {
                            if(selected.value === option.value) {
                                listContent.classList.add("active", "menu-item");
                            }
                        }
                    }
                    listContent.dataset.combobox_list_element = "true";
                    listContent.dataset.value = option.value;
                    listContent.dataset.record = JSON.stringify(option.textContent);
                    listContent.textContent = content;
                    listItem.appendChild(listContent);
                    combobox_dropdown.appendChild(listItem);
                    isOK = true;
                }
            });
        } else {
            isOK = await this.fetchOptions(keyword, this.currentPage);
        }
        if(isOK) combobox_dropdown.classList.remove("hidden");
    }

    onClear(event) {
        event.stopPropagation();

        const combobox_select = this.shadowRoot.getElementById(this.selectTagId);
        const combobox_input = this.shadowRoot.getElementById(this.inputTagId);

        this.value = null;
        this.keyword = null;
        this.selectedItems = [];

        combobox_input.value = null;
        // TODO: test multiple selection clear
        combobox_select.selectedIndex = -1;

        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                key: this.name,
                value: this.value,
                field: this,
                sender: ["Combobox.onClear"]
            }
        }));
    }

    onBlur(event) {
        if(this.disabled) {
            event.preventDefault();
            event.stopPropagation();
            return false;
        }

        this.shadowRoot.getElementById(this.inputDivTagId).classList.remove("border-primary");

        const combobox_dropdown = this.shadowRoot.getElementById(this.dropdownTagId);
        if(combobox_dropdown.classList.contains("hidden")) {
            this.dispatchEvent(new CustomEvent(`form-field-blur-${this.ownerId}`, {
                        bubbles: true,
                        composed: true,
                        detail: { key: this.name }
            }));
            return false;
        }

        /*
            use timeout to allow onOptionClick to fire up if ever
            and we cannot rely on events
            Chromium triggers a FocusEvent while Firefox a blur Event
        */
        // TODO: find a better solution than setTimeout
        setTimeout(() => {
            // default invalid input with last valid selection
            const combobox_select = this.shadowRoot.getElementById(this.selectTagId);
            const combobox_input = this.shadowRoot.getElementById(this.inputTagId);

            if(!this.multiple && combobox_select.options.length > 0) {
                if(isEmpty(combobox_input.value)) {
                    combobox_select.selectedIndex = -1;
                    this.value = null;
                    this.keyword = null;
                    this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                        bubbles: true,
                        composed: true,
                        detail: {
                            key: this.name,
                            value: this.value,
                            field: this,
                            sender: ["Combobox.onBlur"]
                        }
                    }));
                } else if(!isEmpty(this.value) && combobox_select.selectedIndex >= 0) {
                    if(this.fieldType === "Enum") {
                        if(isEmpty(combobox_input.value)  && !isEmpty(combobox_select.value)) {
                            combobox_input.value = JSON.parse(combobox_select.selectedOptions[0].text)[1];
                        } else if(combobox_input.value) {
                            if(combobox_select.selectedOptions[0].text &&
                                combobox_input.value !== JSON.parse(combobox_select.selectedOptions[0].text)[1]) {
                                    combobox_input.value = JSON.parse(combobox_select.selectedOptions[0].text)[1];
                            }
                        }
                    } else {
                        let value = null;
                        if(combobox_select.selectedOptions[0].text) {
                            value = get(JSON.parse(combobox_select.selectedOptions[0].text), this.selectKey);
                        }
                        if(isEmpty(combobox_input.value) && !isEmpty(combobox_select.value)) {
                            combobox_input.value = value;
                        } else if(combobox_input.value) {
                            if(value && combobox_input.value !== value) {
                                combobox_input.value = value;
                            }
                        }
                    }
                } else {
                    combobox_input.value = null;
                    combobox_select.selectedIndex = -1;
                }
            }
            this.clearDropdown();
            // bubble up event to parent Lit form
            this.dispatchEvent(new CustomEvent(`form-field-blur-${this.ownerId}`, {
                        bubbles: true,
                        composed: true,
                        detail: { key: this.name }
            }));
        }, 250);
    }

    setFieldValue(value) {
        // set field data from parent
        const combobox_input = this.shadowRoot.getElementById(this.inputTagId);
        const combobox_select = this.shadowRoot.getElementById(this.selectTagId);

        if(isNil(value)) {
            value = "";
        }
        if(this.multiple) {
            if(isEmpty(value)) {
                this.value = [];
            } else if(!isArray(value)) {
                this.value = [value];
            }
        } else {
            if(!isEmpty(value) && !isEmpty(this.selectKey) &&
                this.selectKey.split(".").length > 1) {
                    //this.value = get(value, this.selectKey.split(".")[0],
                    //        get(this.formData, this.selectKey.split(".")[0], value));
                    this.value = get(value, this.selectKey.split(".")[0], null);
                }
            else this.value = value;
        }
        // select already populated
        if(combobox_select && combobox_select.options.length > 0) {
            let field_value = null;
            if(isObject(this.value)) {
                field_value = this.value;
                if(this.fieldType === "Enum") {
                    if(this.multiple) {
                        this.selectedItems = [];
                        combobox_input.value = "";
                        Array.from(combobox_select.options).forEach((option) => {
                            this.value.forEach(item => {
                                if(item[0] === option.value) {
                                    option.selected = true;
                                    this.selectedItems.push({
                                            "key": option.value,
                                            "text": JSON.parse(option.textContent)[1],
                                            "record": option.textContent
                                    });
                                }
                           });
                        });
                        field_value = [];
                        this.selectedItems.forEach(item => {
                            field_value.push(item.key);
                        });
                    } else {
                        combobox_select.value = this.value[0];
                        combobox_input.value = this.value[1];
                        this.keyword = this.value[1];
                    }
                } else {
                    if(this.multiple) {
                        this.selectedItems = [];
                        combobox_input.value = "";
                        Array.from(combobox_select.options).forEach((option) => {
                            this.value.forEach(item => {
                                const key = get(item, this.selectId);
                                if(key === option.value) {
                                    option.selected = true;
                                    this.selectedItems.push({
                                            "key": option.value,
                                            "text": get(item, this.selectKey),
                                            "record": item
                                    });
                                }
                           });
                        });
                        field_value = [];
                        this.selectedItems.forEach(item => {
                            field_value.push(item.record);
                        });
                    } else {
                        combobox_select.value = get(this.value, this.selectId, "");
                        combobox_input.value = get(this.value, this.selectKey);
                        if(isArray(this.value))
                            this.keyword = this.value[1];
                        else
                            this.keyword = get(this.value, this.selectKey);
                    }
                }
            } else {
                field_value = this.value;
                if(isEmpty(this.value)) {
                    this.keyword = this.value;
                    combobox_input.value = this.keyword;
                } else {
                    combobox_select.value = this.value;
                    this.value = JSON.parse(combobox_select.selectedOptions[0].text);
                    if(this.fieldType === "Enum") {
                        this.keyword = this.value[1];
                        combobox_input.value = this.keyword;
                    } else {
                        this.keyword = get(this.value, this.selectKey);
                        combobox_input.value = this.keyword;
                        if(this.selectKey.split(".").length > 1) {
                            field_value = get(this.value, this.name);
                        }
                    }
                }
            }
            this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                        key: this.name,
                        value: field_value,
                        type: this.fieldType,
                        record: this.value,
                        sender: ["Combobox.setFieldValue"]
                    }
            }));
        } else if(!this.multiple) {  // select not yet populated
            if(isObject(this.value)) {
                if(isArray(this.value))
                    this.keyword = this.value[1];
                else if(this.selectKey.split(".").length > 1) {
                    this.keyword = get(this.value, this.selectKey.split('.').slice(1).join('.'));
                }
                else
                    this.keyword = get(this.value, this.selectKey);
            } else {
                this.keyword = this.value;
            }

            if(combobox_input) combobox_input.value = this.keyword;

            this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                        key: this.name,
                        value: this.value,
                        type: this.fieldType,
                        record: value,
                        sender: ["Combobox.setFieldValue2"]
                    }
            }));
        }
    }

    onRemoveSelection(value) {
        const combobox_select = this.shadowRoot.getElementById(this.selectTagId);
        const optionToDeselect = combobox_select.querySelector(`option[value="${value}"]`);

        if (optionToDeselect) {
            this.selectedItems = this.selectedItems.filter(function(element) {
                return element.key.toString() !== optionToDeselect.value.toString();
            });
            optionToDeselect.selected = false;

            const field_value = [];
            this.selectedItems.forEach(item => {
                if(this.fieldType === "Enum") {
                    field_value.push(item.key);
                } else {
                    field_value.push(item.record);
                }
            });
            this.value = field_value;
            this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    key: this.name,
                    value: field_value,
                    field: this,
                    type: this.fieldType,
                    sender: ["Combobox.onRemoveSelection"]
                }
            }));

            this.requestUpdate();  // force render
        }
    }

    updated() {
        // properties update from parent

        // apply errors from parent
        const error_box = this.shadowRoot.querySelector("[data-error]");
        if(this.errorMessage) {
            error_box.textContent = this.errorMessage;
            error_box.classList.remove("hidden");
            this.shadowRoot.getElementById(this.inputDivTagId).classList.add("border-error");
        } else {
            error_box.textContent = "";
            error_box.classList.add("hidden");
            this.shadowRoot.getElementById(this.inputDivTagId).classList.remove("border-error");
        }
        // this.autoFocus is turned off/on by form validation
        if(this.autoFocus) {
            this.shadowRoot.getElementById(this.inputTagId).focus();
        }
        // register field types
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

    onInputFocus() {
        // input has focus - apply focus to parent div
        this.shadowRoot.getElementById(this.inputDivTagId).classList.add("border-primary");
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
        const inputSizeClass = {
            "w-fit":  this.multiple,
            "w-full": !this.multiple
        };

        const classes = {
            "focus:border-primary": !this.disabled,
            "cursor-not-allowed": this.disabled
        };
        return html`
            ${this.label ?
                html`
                    <label class="label block text-sm font-medium leading-6"
                        for="${this.inputTagId}">
                        <span class="label-text">${this.label}</span>
                    </label>`
            : nothing }
            <div class="${classMap(classes)} select select-bordered relative flex flex-row flex-wrap items-center gap-2 w-full max-w-2xl focus:outline-none"
                    id="${this.inputDivTagId}"
                    tabindex="${this.disabled ? '-1' : '0'}"
                    @blur="${this.onBlur}"
                    @click="${this.onClick}"
            >
                ${this.selectedItems.map(item => html`
                    <div class="badge badge-outline badge-lg gap-2">
                        ${item.text}
                        ${this.disabled ? html`` : html`
                        <span class="btn btn-ghost btn-xs" @click="${() => this.onRemoveSelection(item.key)}">
                            <icon-x class="w-4 h-4"></icon-x>
                        </span>`}
                    </div>
                `)}
                <input type="text" data-combobox-input
                    placeholder="${this.placeHolder}"
                    id="${this.inputTagId}"
                    @blur="${this.onBlur}"
                    @input="${this.onInput}"
                    @click="${this.onClick}"
                    @focus="${this.onInputFocus}"
                    class="border-none focus:outline-none bg-base-100 ${classMap(inputSizeClass)}"

                    ?readonly="${this.readOnly}"
                    ?disabled="${this.disabled}"
                    ?required="${this.required}"
                    ?autofocus="${this.autoFocus}"
                    ?autocomplete="${this.autoComplete}"
                />
                ${!this.disabled && !this.readOnly && !this.required
                    ? html`<button
                        class="absolute inset-y-0 right-10 flex items-center px-2"
                        @click="${this.onClear}"
                    >
                        <icon-x></icon-x>
                    </button>`
                : nothing}
            </div>
            <span data-error="${this.inputTagId}"
                class="hidden block mt-2 text-sm text-red-500 peer-[&:not(:placeholder-shown):not(:focus):invalid]:block">
            </span>
            <ul id="${this.dropdownTagId}"
                @click="${this.onOptionClick}"
                @scroll=${ifDefined(this.fieldType === "Select" ? this.onOptionScroll : undefined)}
                class="menu block shadow-xl max-w-2xl overflow-y-auto hidden"
                style="max-height: 200px">
            </ul>
            <select name="${this.name}" id="${this.selectTagId}" class="hidden"
                ?multiple="${this.multiple}"
            ></select>
        `;
    }
}

customElements.define("ui-combobox", Combobox)


class ComboboxRange extends LitElement {
    static styles = [
        css `
            :host{
                display: block;
            }
        `,
        TWStyles
    ];

    static instanceCounter = 0;

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        label: { type: String },
        name: { type: String },
        value: { type: String },
        fieldType: { attribute: "field-type", type: String },  // Enum or Select
        formData: { attribute: "form-data", type: Object},
        parentRow: { attribute: "parent-row", type: Object },

        autoDefault: { type: Boolean },  // auto default to first entry
        readOnly: { type: Boolean },
        disabled: { type: Boolean },
        required: { type: Boolean },
        autoFocus: { attribute: "autofocus", type: Boolean },

        // Select options
        selectTable: { type: String },  // Tablename - used for server update
        selectObject: { type: String },  // Tablename - used for client selection list
        joinList: { type: Array },
        selectId: { type: String },     // FieldName of Tablename Primary Key
        selectKey: { type: String },    // FieldName of Tablename Description to search
        selectColumn: { type: String },  // Datatable selection criteria Column name (non join field)
        selectFormat: { type: Array }, // List of FieldNames for dropdown Display
        selectCascade: { type: Array }, // Array of {field: FieldName, value:}
        // Additional Filter
        validValues: { type: Array }, // Array of valid values
        validValuesKey: { type: String }, // Fieldname for validValues else selectKey
        selectField: { type: String }, // FieldName
        selectFieldValue: { type: String }, // Value FieldName
        selectTableFieldValue: { type: Array },  // Array of {field: FieldName, value:}
        selectGetter: { type: String },  // getter url instead of /list

        // Enum options
        choicesGetter: { attribute: "enum-getter", type: String },
        choices: { type: Object },  // Enum json object (tuple of 2), instead of selectTable

        validators: { type: Array },
        validator_fields: { attribute: "validator-fields", type: Array },
        validator_messages: { attribute: "validator-messages", type: Array }
    };

    constructor() {
        super();
        this.instanceId = "ComboboxRange-" + (++ComboboxRange.instanceCounter).toString();

        // bind the event listener to reference the component instance
        this.handleFieldUpdate = this.handleFieldUpdate.bind(this);
        this.handleFieldBlur = this.handleFieldBlur.bind(this);

        this.ownerId = null;
        this.label = null;
        this.fieldType = null;
        this.value = null;
        this.fromValue = "";
        this.toValue = "";
        this.formData = null;
        this.parentRow = null;

        this.selectTable = null;
        this.selectObject = null;
        this.joinList = null;
        this.selectId = null;
        this.selectKey = null;
        this.selectColumn = null;
        this.selectFormat = null;
        this.validValues = null;
        this.validValuesKey = null;
        this.selectField = null;
        this.selectFieldValue = null;
        this.selectTableFieldValue = null;
        this.selectCascade = null;
        this.selectGetter = null;

        this.choices = null;
        this.choicesGetter = null;

        this.autoDefault = false;
        this.readOnly = false;
        this.disabled = false;
        this.required = false;
        this.autoFocus = false;

        this.validators = null;
        this.validator_fields = null;
        this.validator_messages = null;

        this.addEventListener(`form-field-updated-${this.instanceId}`, this.handleFieldUpdate);
        this.addEventListener(`form-field-blur-${this.instanceId}`, this.handleFieldBlur);
    }

    connectedCallback() {
        super.connectedCallback();

        if(this.value) {
            // remove quotes in string if ever
            const parts = this.value.trim().replace(/^"|"$/g, '').split(',');
            this.fromValue = (parts[0] || '').trim();
            this.toValue = (parts[1] || '').trim();
        }

        if(isNull(this.fieldType)) {
            if(this.choices || this.choicesGetter)  this.fieldType = "Enum";
            else this.fieldType = "Select";
        }
    }

    handleFieldUpdate(event) {
        let field_value = null;
        if(this.fieldType === "Enum") {
            field_value = event.detail.value;
        } else {
            field_value = get(event.detail.value, this.selectKey, "");
        }

        if(event.detail.key.startsWith("From.")) {
            this.fromValue = field_value;
        } else this.toValue = field_value;
    }

    handleFieldBlur(event) {
        this.value = `${this.fromValue},${this.toValue}`;

        this.dispatchEvent(new CustomEvent(`form-field-updated-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                key: this.name,
                value: this.value,
                sender: ["ComboboxRange.handleFieldBlur"]
            }
        }));

        this.dispatchEvent(new CustomEvent(`form-field-blur-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: { key: this.name }
        }));
    }

    render() {
        return html`
            <div class="form-control" style="display: block">
            ${this.label ?
                html`
                    <label class="label block text-sm font-medium leading-6"
                        for="${`From.${this.name}`}">
                        <span class="label-text">${this.label}</span>
                    </label>`
            : nothing }
            <div class="form-control grid grid-cols-2 gap-2">
                <ui-combobox
                    placeholder="From"
                    name="${`From.${this.name}`}"
                    id="${`From.${this.name}`}"
                    owner-id="${this.instanceId}"

                    selectTable="${this.selectTable}"
                    selectObject="${this.selectObject}"
                    joinList='${JSON.stringify(this.joinList)}'
                    selectId="${this.selectId}"
                    selectKey="${this.selectKey}"
                    selectColumn='${JSON.stringify(this.selectColumn)}'
                    selectFormat='${JSON.stringify(this.selectFormat)}'
                    validValues='${JSON.stringify(this.validValues)}'
                    validValuesKey='${JSON.stringify(this.validValuesKey)}'
                    selectField="${this.selectField}"
                    selectFieldValue="${this.selectFieldValue}"
                    selectTableFieldValue='${JSON.stringify(this.selectTableFieldValue)}'
                    selectGetter="${this.selectGetter}"

                    choices='${JSON.stringify(this.choices)}'
                    enum-getter='${JSON.stringify(this.choicesGetter)}'

                    field-type="${this.fieldType}"
                    value="${this.fromValue}"
                    form-data='${JSON.stringify(this.formData)}'
                    validators="${JSON.stringify(this.validators)}"
                    parent-row='${JSON.stringify(this.parentRow)}'

                    ?autofocus="${this.autoFocus}"
                    ?required="${this.required}"
                    ?disabled="${this.disabled}"
                    ?autoDefault="${this.autoDefault}"
                    ?disabled="${this.disabled}"

                ></ui-combobox>
                <ui-combobox
                    placeholder="To"
                    name="${`To.${this.name}`}"
                    id="${`To.${this.name}`}"
                    owner-id="${this.instanceId}"

                    selectTable="${this.selectTable}"
                    selectObject="${this.selectObject}"
                    joinList='${JSON.stringify(this.joinList)}'
                    selectId="${this.selectId}"
                    selectKey="${this.selectKey}"
                    selectColumn='${JSON.stringify(this.selectColumn)}'
                    selectFormat='${JSON.stringify(this.selectFormat)}'
                    validValues='${JSON.stringify(this.validValues)}'
                    validValuesKey='${JSON.stringify(this.validValuesKey)}'
                    selectField="${this.selectField}"
                    selectFieldValue="${this.selectFieldValue}"
                    selectTableFieldValue='${JSON.stringify(this.selectTableFieldValue)}'
                    selectGetter="${this.selectGetter}"

                    choices='${JSON.stringify(this.choices)}'
                    enum-getter='${JSON.stringify(this.choicesGetter)}'

                    field-type="${this.fieldType}"
                    value="${this.toValue}"
                    form-data='${JSON.stringify(this.formData)}'
                    validators="${JSON.stringify(this.validators)}"
                    parent-row='${JSON.stringify(this.parentRow)}'

                    ?required="${this.required}"
                    ?disabled="${this.disabled}"
                    ?autoDefault="${this.autoDefault}"
                    ?disabled="${this.disabled}"

                ></ui-combobox>
                <p data-error="${this.name}"
                    class="col-span-2 hidden block mt-2 text-sm text-red-500 peer-[&:not(:placeholder-shown):not(:focus):invalid]:block">
                </p>
            </div>
        `;
    }
}

customElements.define("ui-combobox-range", ComboboxRange)
