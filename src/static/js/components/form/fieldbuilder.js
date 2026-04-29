import api from "../../api"
import store from "../../store"
import { get, isEmpty, isNull } from "../../utils"

export function buildField(field, index, formData, parentRow, mode) {
    const value = get(formData, field.name, "");

    switch(field.type) {
        case "DataTable":
            let div = document.createElement('div');
            div.innerHTML = `<p>Field ${field.type} ${field.name}</p>`;
            return div;
        case "Select":
            const combo = document.createElement(field.range ? "ui-combobox-range" : "ui-combobox");
            combo.name = field.name;
            combo.label = field.label;
            combo.selectTable = field.selectTable;
            combo.selectObject = field.selectObject;
            combo.joinList = field.join_list;
            combo.selectId = field.selectId;
            combo.selectKey = field.selectKey;
            combo.selectColumn = field.selectColumn;
            combo.selectFormat = field.selectFormat;
            combo.validValues = field.validValues;
            combo.validValuesKey = field.validValueKeys;
            combo.selectField = field.selectField;
            combo.selectFieldValue = field.selectFieldValue;
            combo.selectTableFieldValue = field.selectTableFieldValue;
            combo.selectGetter = field.selectGetter;
            combo.autoFocus = index === 0 ? true : false;
            combo.required = field.required;
            combo.disabled = mode === "Delete";
            combo.validator = field.validator;
            combo.formData = formData;
            combo.parentRow = parentRow;
            combo.fieldType = field.type;
            combo.multiple = field.use_list;
            if(!isEmpty(field.autoDefault)) combo.autoDefault = field.autoDefault;
            else if(!isEmpty(field.requiredIf) && field.required) combo.autoDefault = true;
            if(!isEmpty(formData) && !isEmpty(field.selectObject) &&
                field.selectTable !== field.selectObject) {
                combo.value = JSON.stringify(formData);
            } else if (!isEmpty(value)) {
                combo.value = JSON.stringify(value);
            }
            return combo;
        case "Enum":
            const choice = document.createElement(field.range ? "ui-combobox-range" : "ui-combobox");
            choice.name = field.name;
            choice.label = field.label;
            choice.autoFocus = index === 0 ? true : false;
            choice.required = field.required;
            choice.disabled = mode === "Delete";
            choice.validator = field.validator;
            choice.formData = formData;
            choice.parentRow = parentRow;
            choice.validValues = field.validValues;
            choice.validValuesKey = field.validValueKeys;
            if(field.enums) choice.choices = field.enums;
            else choice.choicesGetter = field.enum_getter;
            choice.fieldType = field.type;
            choice.multiple = field.use_list;
            if(!isEmpty(field.autoDefault)) choice.autoDefault = field.autoDefault;
            else if(!isEmpty(field.requiredIf) && field.required) choice.autoDefault = true;
            if(!isEmpty(value)) {
                choice.value = JSON.stringify(value);
            }
            return choice;
        case "Boolean":
            const checkbox = document.createElement("ui-checkbox");
            checkbox.name = field.name;
            checkbox.label = field.label;
            checkbox.autoFocus = index === 0 ? true : false;
            checkbox.disabled = mode === "Delete";
            checkbox.validator = field.validator;
            checkbox.value = value;
            return checkbox;
        case "Date":
            const date = document.createElement("ui-datetime");
            date.name = field.name;
            date.label = field.label;
            //date.type = "text"  // text or hidden
            date.fieldType = field.type;
            date.mode = field.dateMode;  // single/range/multiple
            date.autoFocus = index === 0 ? true : false;
            date.required = field.required;
            date.disabled = mode === "Delete";
            date.validator = field.validator;
            if(!isEmpty(field.autoDefault)) date.defaultDate = field.autoDefault;
            else if(!isEmpty(field.requiredIf) && field.required) date.defaultDate = true;
            // see date-fns unicode token for date format
            date.value = value; // string or date yyyy-MM-dd - 2025-01-31
            return date;
        case "Time":
            const time = document.createElement("ui-datetime");
            time.name = field.name;
            time.label = field.label;
            //time.type = "text"  // text or hidden
            time.fieldType = field.type;
            time.mode = field.dateMode;  // single/range/multiple
            time.autoFocus = index === 0 ? true : false;
            time.required = field.required;
            time.disabled = mode === "Delete";
            time.validator = field.validator;
            if(!isEmpty(field.autoDefault)) time.defaultDate = field.autoDefault;
            else if(!isEmpty(field.requiredIf) && field.required) time.defaultDate = true;
            // see date-fns unicode token for datetime format
            time.value = value; // yyyy-MM-dd'T'HH:mm:ss  - 2025-01-31T14:50:10
            return time;
        case "DateTime":
            const datetime = document.createElement("ui-datetime");
            datetime.name = field.name;
            datetime.label = field.label;
            //datetime.type = "text"  // text or hidden
            datetime.fieldType = field.type;
            datetime.mode = field.dateMode;  // single/range/multiple
            datetime.autoFocus = index === 0 ? true : false;
            datetime.required = field.required;
            datetime.disabled = mode === "Delete";
            datetime.validator = field.validator;
            if(!isEmpty(field.autoDefault)) datetime.defaultDate = field.autoDefault;
            else if(!isEmpty(field.requiredIf) && field.required) datetime.defaultDate = true;
            // see date-fns unicode token for datetime format
            datetime.value = value; // yyyy-MM-dd'T'HH:mm:ssXXX - 2025-01-31T14:50:10GMT+11
            return datetime;
        case "File":
            const file = document.createElement("ui-input");
            file.name = field.name;
            file.label = field.label;
            file.type = "file";
            file.required = field.required;
            file.accept = field.accept;
            file.fileReaderOnLoadHandler = field.onLoadHandler;
            return file;
        case "Integer":
        case "BigInteger":
        case "Numeric":
            const number = document.createElement("ui-input");
            number.name = field.name;
            number.label = field.label;
            number.type = "number";
            number.fieldType = field.type;
            number.autoFocus = index === 0 ? true : false;
            number.required = field.required;
            number.disabled = mode === "Delete";
            number.validator = field.validator;
            number.value = value;
            number.multiple = field.multiple;
            number.range = field.range;
            return number;
        case "Hidden":
            const hide = document.createElement("ui-input");
            hide.name = field.name;
            hide.type = "hidden";
            hide.fieldType = field.type;
            hide.value = value;
            return hide;
        default:
            const text = document.createElement("ui-input");
            text.name = field.name;
            text.label = field.label;
            text.type = "text";
            text.fieldType = field.type;
            text.maxLength = field.length;
            text.autoFocus = index === 0 ? true : false;
            text.required = field.required;
            text.disabled = mode === "Delete";
            text.validator = field.validator;
            text.value = value;
            text.multiple = field.multiple;
            text.range = field.range;
            return text;
    }
}
