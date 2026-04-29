import * as Yup from 'yup';
import { format, parse, isDate } from "date-fns";

import { get, set, tokenizer, isEmpty, isNil, isNull, isArray, isObject,
        dateTimeFormat, dateTimeFormatTZ } from "../../utils"

export function FormTitle(title, titleFields, data, keyTitle) {
    if(title && !isEmpty(data)) {
        if(!isNull(titleFields)) {
            let key_title = "";
            titleFields.forEach((key, keyidx) => {
                if(isArray(key)) {
                    let title_str = "";
                    key.forEach((val, idx) => {
                        title_str += ` ${get(data, val, "")}`;
                    });
                    if(!isEmpty(title_str.trim())) {
                        if(keyidx > 0) key_title += ` : `;
                        key_title += ` ${title_str}`;
                    }
                } else {
                    key_title += ` ${get(data, key, "")}`;
                }
            });
            if(!isEmpty(key_title.trim())) title += ` - ${key_title}`;
        } else if(keyTitle) {
            const key_value = get(data, keyTitle, null);
            if(!isEmpty(key_value)) title += ` - ${key_value}`;
        }
    }
    return title;
}

export function ConvertToFormValues(types, values, locale, timezone) {
    // convert data to form data
    /**
    Object.keys(types).forEach(key => {
        const field_value = get(values, key);
        if(!isEmpty(field_value)) {
        }
    });
    **/
    return values;
}


export function ConvertToJsonValues(types, values, locale, timezone) {
    // convert data for json transport
    Object.keys(types).forEach(key => {
        const field_value = get(values, key);

        if(types[key] === "Enum"  && isArray(field_value)) {
            set(values, key, field_value[0]);
        } else if(types[key] === "Date") {
            // if field_value is string then already in ISO date string
            if(!isNil(field_value) && typeof field_value !== 'string') {
                // field_value is a date - convert to ISO date string
                set(values, key, format(field_value,"yyyy-MM-dd"));
            }
        } else if(types[key] === "Time") {
            // if field_value is string then already in ISO datetime string
            if(!isNil(field_value) && typeof field_value !== 'string') {
                // field_value is a date - convert to ISO datetime string
                set(values, key, format(field_value,"yyyy-MM-dd'T'HH:mm:ss"));
            }
        } else if(types[key] === "DateTime") {
            // if field_value is string then already in ISO datetime tz string
            if(!isNil(field_value) && typeof field_value !== 'string') {
                // field_value is a datetime - convert to ISO datetime tz string
                // yyyy-MM-dd'T'HH:mm:ssXXX
                set(values, key, dateTimeFormatTZ(field_value, locale, timezone));
            }
        }
    });
    return values;
}

export function ActionOn(panel_fields, base_field, value) {
    if(!isEmpty(base_field.actionOn)) {
        // convert "value || base_field.default" to string use ?: in case of boolean
        const val = String(isEmpty(value) ? base_field.default : value);
        if(val in base_field.actionOn) {
            Object.keys(panel_fields).forEach(field_name => {
                if(base_field.actionOn[val].onFields.includes(field_name)) {
                    if(panel_fields[field_name].isLit)
                        panel_fields[field_name].node.hide(false);
                    else
                        panel_fields[field_name].style.display = "block";
                } else if(base_field.actionOn[val].offFields.includes(field_name)) {
                    if(panel_fields[field_name].isLit)
                        panel_fields[field_name].node.hide(true);
                    else
                        panel_fields[field_name].style.display = "none";
                }
            });
        }
    }
}

export function Cascade(form, field, value) {
    if(!isEmpty(field.selectCascade) && !isNull(value)) {
        field.selectCascade.forEach(ele => {
            let val = isEmpty(value) ? "" : value;
            if(ele.value !== ".") {  // not current table
                if(isObject(value) && !isEmpty(value)) val = get(value, ele.value);
            }
            form.setFieldValue(ele.field, val);
        });
    }
}

export function parse_expression(expression) {
    const word_operators = [ "in", "and", "or" ];

    const express_tokens = tokenizer(expression);

    let start = true;
    let token_field = [];
    let token_op = [];
    let token_obj = [];
    let token_cond = [];
    let idx = -1;

    express_tokens.forEach(token => {
        if(token.type !== "whitespace") {
            if(start) {
                idx = idx + 1;
                token_field.push("");
                token_op.push("");
                token_obj.push("");
                token_cond.push("");
                start = false;
            }
            if(token.type === "word" && isEmpty(token_field[idx])) {
                token_field[idx] = token.token;
            } else if(token.type === "word" && word_operators.includes(token.token)) {
                if(token.token === "and" || token.token === "or") {
                    start = true;
                    token_cond[idx] = token.token === "and" ? "&&" : "||";
                } else {
                    token_op[idx] = token.token;
                }
            } else if(token.type === "operators") {
                if(token.token === "&&" || token.token === "||") {
                    start = true;
                    token_cond[idx] = token.token;
                } else if(token.token === "=") {
                    token_op[idx] = "===";
                } else {
                    token_op[idx] = token.token;
                }
            } else if(token.type === "punctuation" &&
                        ["+","-","*","/"].includes(token.token)) {
                start = true;
                token_op[idx] = token.token;
            } else {
                token_obj[idx] = token_obj[idx] + token.token;
            }
        }
    });

    let return_string = "";
    for(let i = 0;i < token_field.length;i++) {
        if(token_op[i] === "in") {
            return_string = return_string.trim() + " " +
                            token_obj[i].replace("(","[").replace(")","]").trim() +
                            ".includes(" + token_field[i].trim() + ") " +
                            token_cond[i].trim();
        } else {
            return_string = return_string.trim() + " " +
                            token_field[i].trim() + " " +
                            token_op[i].trim() + " " +
                            token_obj[i].trim() + " " +
                                    token_cond[i].trim();
        }
    }

    return [token_field, return_string];
}

function ValidatorMessage(field, type, message) {
    if(field.validator_messages) {
        const obj = field.validator_messages.find(obj => obj.hasOwnProperty(type));
        if(obj) message = obj[type];
    }
    return message;
}

function EnumRequired(field, val_object, message) {
    message = ValidatorMessage(field, "Required", message);
    return val_object.test({
        test: value => !isEmpty(value) && !isEmpty(value[0]),
        message: message || `${field.label} is required`
    });
}

function EnumEqualTo(field, val_object, equal_type) {
    // equal_type = "EqualTo", "NotEqualTo"
    const message = ValidatorMessage(field, equal_type, null);
    let equal_fields = null;
    if(field.validator_fields) {
        const obj = field.validator_fields.find(obj => obj.hasOwnProperty(equal_type));
        if(obj) {
            /**
                Yup v0.32 (and earlier versions) doesn't preserve nested paths
                like "Params.fromcompany" inside this.parent.
                It only gives you the immediate parent object of the current field
                — that would be the Params object.
            **/
            equal_fields = obj[equal_type].split('.').pop();  // fromcompany
        }
    }
    if(equal_type === "NotEqualTo")
        return val_object.test({
            test: function(value) {
                const target = this.parent[equal_fields];
                return value[0] !== target[0];
            },
            message: message || `${field.label} is equal to ${equal_fields}`
        });
    else
        return val_object.test({
            test: function(value) {
                const target = this.parent[equal_fields];
                return value[0] === target[0];
            },
            message: message || `${field.label} is not equal to ${equal_fields}`
        });
}

function SelectRequired(field, val_object, message) {
    message = ValidatorMessage(field, "Required", message);
    if(field.use_list) {
        return val_object.test({
                test: value => !isNil(value) && value.length > 0,
                message: message || `${field.label} is required`
        });
    } else {
        return val_object.test({
            test: value => !isNil(value) && Object.keys(value).length > 0,
            message: message || `${field.label} is required`
        });
    }
}

function RequiredIf(val_obj, field, fields) {
    if(isEmpty(field.requiredIf)) return null;
    const expr = parse_expression(field.requiredIf);

    let required = null;
    let required_message = ValidatorMessage(field, "RequiredIf", `${field.label} is Required`);
    if(field.listFormat) {
        required = val_obj.min(1, required_message);
    } else if(field.type === "Enum") {
        required = EnumRequired(field, val_obj, required_message);
    } else if(field.type === "Select") {
        required = SelectRequired(field, val_obj, required_message);
    } else if(["Numeric","Integer","BigInteger"].includes(field.type)) {
        required_message = ValidatorMessage(field, "Required", required_message);
        required = val_obj.notZero(required_message);
    } else {
        required_message = ValidatorMessage(field, "Required", required_message);
        required = val_obj.required(required_message);
    }

    let token_string = expr[0].toString();
    // convert token_string to array
    let token = null;
    if(token_string.indexOf(",") > -1) {
        token = token_string.split(',').map(item => {
            if(item.indexOf(".") > -1) {
                // use context - Yup 0.32.11 cannot handle complex dotNotation ie: Params.maps.data.field_action_0
                // $ is specific to Yup to reference context values.
                const tok = "$" + item.replaceAll(".", "_").trim();
                expr[1] = expr[1].replaceAll(item, tok);
                return tok;
            } else {
                return item.trim();
            }
        });
    } else {
        if(token_string.indexOf(".") > -1) {
            // use context - Yup 0.32.11 cannot handle complex dotNotation ie: Params.maps.data.field_action_0
            // $ is specific to Yup to reference context values.
            const tok = "$" + token_string.replaceAll(".", "_").trim();
            expr[1] = expr[1].replaceAll(token_string, tok);
            token = [tok];
        } else {
            token = [token_string.trim()];
        }
    }
    return val_obj.when(token, {
        //is: new Function(token, `console.log("requiredIf: ${token}", ${token}, ${expr[1]}); return ${expr[1]};`),
        is: new Function(token, `return ${expr[1]};`),
        then: required
    });
}

function NodeValidationType(type) {
    switch(type) {
        case "button":
        case "submit":
        case "reset":
        case "hidden":
            return null;
        case "checkbox":
            return "Boolean";
        case "date":
            return "Date";
        case "datetime-local":
            return "Datetime";
        case "time":
            return "Time";
        case "number":
            return "Numeric";
        case "textarea":
            return "Text";
        case "file":
            return "File";
        default:
            return "String";
    }
}

export function ExtractNodeValidators(node, isLit=false) {
    let element = null;
    if(isLit && node.fieldType) {
        element = {"name": node.name, "type": node.fieldType, "label": node.label };
    } else {
        const typ = NodeValidationType(node.type);
        if(typ) {
            element = {"name": node.name, "type": typ, "label": node.label };
        }
    }
    if(element) {
        element["required"] = node.required ? true : false;
        element["required_message"] = node.getAttribute("required") ? node.getAttribute("required") : node.name + " is Required";
        element["integer_message"] = node.integerMessage ? node.integerMessage : node.name + " must be Integer";
        element["email_message"] = node.emailMessage ? node.emailMessage : "Invalid Email";

        element["length"] = node.maxLength;
        element["min"] = node.min;
        element["max"] = node.max;

        element["use_list"] = node.multiple ? true : false;
        element["listFormat"] = false;

        const validators = !isNil(node.validators) && isArray(node.validators) ? node.validators : [];
        if(node.type === "email") {
            if(!"Email".includes(validators)) {
                validators.push("Email");
            }
        }

        element["validators"] = validators;
        element["validator_fields"] = !isNil(node.validator_fields) && isArray(node.validator_fields) ? node.validator_fields : [];
        element["validator_messages"] = !isNil(node.validator_messages) && isArray(node.validator_messages) ? node.validator_messages : [];
    }
    return element;
}

export function ExtractFieldValidators(field) {
    const element = field;

    element["required_message"] = `${field.label ? field.label : "Field"} is Required`;
    element["integer_message"] = `${field.label ? field.label : "Field"} must be Integer`;
    element["email_message"] = "Invalid Email";

    const validators = !isNil(field.validators) && isArray(field.validators) ? field.validators : [];
    if(field.type === "email") {
        if(!"Email".includes(validators)) {
            validators.push("Email");
        }
    }
    if(!isNil(field.validators) && isArray(field.validators)) {
        field.validators.forEach(val => {
            validators.push(val);
        });
    }

    element["validators"] = validators;
    element["validator_fields"] = !isNil(field.validator_fields) && isArray(field.validator_fields) ? field.validator_fields : [];
    element["validator_messages"] = !isNil(field.validator_messages) && isArray(field.validator_messages) ? field.validator_messages : [];

    return element;
}

export function ValidateFields(form) {
    if (form.validationSchema) {
        Object.keys(form.fieldNodes).forEach(fieldName => {
            form.errors[fieldName] = "";
            if(form.fieldNodes[fieldName].isLit) {
                form.fieldNodes[fieldName].node.errorMessage = "";
                form.fieldNodes[fieldName].node.autoFocus = false;
            } else {
                form.fieldNodes[fieldName].node.classList.remove("border-error");
                if(fieldName in form.errorMessageNodes) {
                    form.errorMessageNodes[fieldName].classList.add("hidden");
                }
            }
        });
        if(!isNil(form.submitButton)) {
            form.submitButton.disabled = false;
        }
        // bubble up event to owner
        form.dispatchEvent(new CustomEvent(`submit-button-disable-${form.ownerId}`, {
                bubbles: true,
                composed: true,
                detail: {
                    value: false,
                    buttonText: null
                }
        }));

        const context = CreateValidationContext(form.fieldNodes, form.formData);
        try {
            form.validationSchema.validateSync(form.formData,
                { strict: false, abortEarly: false, stripUnknown: true, recursive: true,
                  context: context});
        } catch (error) {
            let index = 0;  // to determine autofocus
            let fieldError = false;
            // field error
            Object.keys(form.fieldNodes).forEach(fieldName => {
                const fieldErrors = error.inner.filter((err) => err.path === fieldName);
                if (fieldErrors.length > 0) {
                    fieldError = true;
                    fieldErrors.forEach(field => {
                        if(field.message !== undefined) {
                            form.errors[fieldName] = field.message;
                            if(form.fieldNodes[fieldName].isLit) {
                                form.fieldNodes[fieldName].node.errorMessage =
                                    form.fieldNodes[fieldName].node.errorMessage +
                                   (form.fieldNodes[fieldName].node.errorMessage ? "<br />" : "") +
                                    form.errors[fieldName];
                            } else {
                                form.errorMessageNodes[fieldName].classList.remove("hidden");
                                form.errorMessageNodes[fieldName].textContent =
                                    form.errorMessageNodes[fieldName].textContent +
                                   (form.errorMessageNodes[fieldName].textContent ? "<br />" : "") +
                                    field.message;
                                form.fieldNodes[fieldName].node.classList.add("border-error");
                            }
                            if(index === 0 && !form.errorFocused) {
                                form.fieldNodes[fieldName].node.autoFocus = true;
                                // autofocus once only
                                form.errorFocused = true;
                            } else {
                                form.fieldNodes[fieldName].node.autoFocus = false;
                            }
                        }
                        index += 1;
                    });
                    if(!isNil(form.submitButton)) {
                        form.submitButton.disabled = true;
                    }
                    // bubble up event to owner
                    form.dispatchEvent(new CustomEvent(`submit-button-disable-${form.ownerId}`, {
                        bubbles: true,
                        composed: true,
                        detail: {
                            value: true,
                            buttonText: null
                        }
                    }));
                }
            });
            // form error
            if(!fieldError) {
                Object.keys(form.fieldNodes).forEach(fieldName => {
                    if(form.fieldNodes[fieldName].isLit) {
                        if(!form.errorFocused) {
                            form.fieldNodes[fieldName].node.autoFocus = true;
                            // autofocus once only
                            form.errorFocused = true;
                        } else {
                            form.fieldNodes[fieldName].node.autoFocus = false;
                        }
                    }
                });
                if(!isNil(form.submitButton)) {
                    form.submitButton.disabled = true;
                }
                // bubble up event to owner
                form.dispatchEvent(new CustomEvent(`submit-button-disable-${form.ownerId}`, {
                        bubbles: true,
                        composed: true,
                        detail: { value: true }
                }));
                const toaster = document.querySelector("[data-toaster]");
                toaster.show(error,"error");
            }
            return false;
        }
    }
    return true;
}

export function CreateValidationContext(fieldNodes, formData) {
    /*
        Yup 0.32.11 cannot handle complex dotNotation Strings in .when()
        ie: Params.maps.data.field_action_0[0]
    */
    const context = {};
    Object.keys(fieldNodes).forEach(key => {
        let value = get(formData, key, null);
        if(!isNull(value)) {
            let name = key.replaceAll(".", "_"); // see RequiredIf context above
            context[name] = value;
        }
    });
    return context;
}

export function CreateFormValidator(func, fieldNodes, val_obj) {
    return func(fieldNodes, val_obj);
}

export function CreateValidationSchema(fields, cyclic_fields=null, validation_schema=null) {
    const schemas = {};
    fields.forEach(field => {
        let required_if = null;
        let val_object = null;

        let message = null;
        let equal_fields = null;

        switch(field.type) {
            case "DataTable":
                val_object = Yup.array().ensure();

                required_if = RequiredIf(val_object, field, fields);
                if(required_if) {
                    val_object = required_if;
                } else if(field.required) {
                    message = ValidatorMessage(field, "Required", field.required_message);
                    val_object = val_object.of(Yup.string().required(message));
                }
                if(field.min) {
                    message = ValidatorMessage(field, "Min", null);
                    val_object = val_object.test({
                        test: value => value.length >= field.min,
                        message: message || `${field.label} Minimum {field.min} row/s exceeded`
                    });
                }
                if(field.max) {
                    message = ValidatorMessage(field, "Max", null);
                    val_object = val_object.test({
                        test: value => value.length <= field.max,
                        message: message || `${field.label} Maximum {field.max} row/s exceeded`
                    });
                }
                break;
            case "Enum":
                if(field.use_list) val_object = Yup.array().ensure();
                else if(isArray(field.default)) val_object = Yup.array().ensure();
                else val_object = Yup.string().ensure();

                required_if = RequiredIf(val_object, field, fields);
                if(required_if) {
                    val_object = required_if;
                } else if(field.required) {
                    message = ValidatorMessage(field, "Required", field.required_message);
                    val_object = EnumRequired(field, val_object, message);
                }

                if(field.validators && field.validators.includes("EqualTo")) {
                    val_object = EnumEqualTo(field, val_object, "EqualTo");
                }
                if(field.validators && field.validators.includes("NotEqualTo")) {
                    val_object = EnumEqualTo(field, val_object, "NotEqualTo");
                }

                break;
            case "Select":
                if(field.use_list) val_object = Yup.array().ensure();
                else val_object = Yup.mixed().nullable().transform((value, orig) => (value) ? value : {});
                //else val_object = Yup.object().nullable().transform((value, orig) => (value) ? value : {});

                if(!field.listFormat) {
                    required_if = RequiredIf(val_object, field, fields);
                    if(required_if) {
                        val_object = required_if;
                    } else if(field.required) {
                        message = ValidatorMessage(field, "Required", field.required_message);
                        val_object = SelectRequired(field, val_object, message);
                    }
                }
                break;
            case "Boolean":
                val_object = Yup.boolean().nullable().transform((value, orig) => isEmpty(orig) ? false : value);

                if(!field.listFormat) {
                    required_if = RequiredIf(val_object, field, fields);
                    if(required_if) {
                        val_object = required_if;
                    } else if(field.required) {
                        message = ValidatorMessage(field, "Required", field.required_message);
                        val_object = val_object.required(message);
                    }
                }
                break;
            case "Integer":
            case "BigInteger":
            case "Numeric":
                //val_object = Yup.number().nullable().transform((value, orig) => Number.isNaN(value) ? 0 : value);
                val_object = Yup.number().nullable().transform((value, orig) => isNaN(Number(value)) ? 0 : value);

                if(["Integer", "BigInteger"].includes(field.type)) {
                    message = ValidatorMessage(field, "Integer", field.integer_message);
                    val_object = val_object.integer(message);
                }
                if(!field.listFormat) {
                    required_if = RequiredIf(val_object, field, fields);
                    if(required_if) {
                        val_object = required_if;
                    } else if(field.required) {
                        message = ValidatorMessage(field, "Required", field.required_message);
                        val_object = val_object.required(message);
                    }
                }

                if(field.validators && field.validators.includes("Positive")) {
                    message = ValidatorMessage(field, "Positive", null);
                    val_object = val_object.positive(message);
                }
                if(field.validators && field.validators.includes("ZeroPositive")) {
                    message = ValidatorMessage(field, "ZeroPositive", null);
                    val_object = val_object.zeroPositive(message);
                }
                if(field.validators && field.validators.includes("Negative")) {
                    message = ValidatorMessage(field, "Negative", null);
                    val_object = val_object.negative(message);
                }
                if(field.validators && field.validators.includes("ZeroNegative")) {
                    message = ValidatorMessage(field, "ZeroNegative", null);
                    val_object = val_object.zeroNegative(message);
                }
                if(field.validators && field.validators.includes("NotZero")) {
                    message = ValidatorMessage(field, "NotZero", null);
                    val_object = val_object.notZero(message);
                }
                if(field.validators && field.validators.includes("Total")) {
                    let total_fields = null;
                    if(field.validator_fields) {
                        const obj = field.validator_fields.find(obj => obj.hasOwnProperty("Total"));
                        if(obj) total_fields = obj["Total"];
                    }
                    message = ValidatorMessage(field, "Total", "Invalid Sum of Totals");
                    val_object = val_object.total(total_fields, message);
                }

                if(field.min) {
                    message = ValidatorMessage(field, "Min", `Exceeded Minimum Value: ${field.min}`);
                    val_object = val_object.min(field.min, message);
                }
                if(field.max) {
                    message = ValidatorMessage(field, "Max", `Exceeded Maximum Value: ${field.max}`);
                    val_object = val_object.max(field.max, message);
                }

                break;
            case "DateTime":
            case "Time":
            case "Date":
                val_object = Yup.date().nullable().transform((value, orig) => isDate(orig) ? value : null);

                if(!field.listFormat) {
                    required_if = RequiredIf(val_object, field, fields);
                    if(required_if) {
                        val_object = required_if;
                    } else if(field.required) {
                        message = ValidatorMessage(field, "Required", field.required_message);
                        val_object = val_object.required(message);
                    }
                }

                break;
            case "File":
                val_object = Yup.mixed().nullable().transform((value, orig) => (value) ? value : {});

                required_if = RequiredIf(val_object, field, fields);
                if(required_if) {
                    val_object = required_if;
                } else if(field.required) {
                    message = ValidatorMessage(field, "Required", field.required_message);
                    val_object = SelectRequired(field, val_object, message);;
                }

                break;
            default:
                val_object = Yup.string().ensure();

                if(field.validators && field.validators.includes("Email")) {
                    message = ValidatorMessage(field, "Email", null);
                    val_object = val_object.email(message);
                }

                if(!field.listFormat) {
                    required_if = RequiredIf(val_object, field, fields);
                    if(required_if) {
                        val_object = required_if;
                    } else if(field.required) {
                        message = ValidatorMessage(field, "Required", field.required_message);
                        val_object = val_object.required(message);
                    }

                    if(!["Text"].includes(field.type)) {
                        if(field.validators && field.validators.includes("EqualTo")) {
                            message = ValidatorMessage(field, "EqualTo", null);
                            equal_fields = null;
                            if(field.validator_fields) {
                                const obj = field.validator_fields.find(obj => obj.hasOwnProperty("EqualTo"));
                                if(obj) equal_fields = obj["EqualTo"];
                            }
                            val_object = val_object.equalTo(equal_fields, message);
                        }
                        if(field.validators && field.validators.includes("NotEqualTo")) {
                            message = ValidatorMessage(field, "NotEqualTo", null);
                            equal_fields = null;
                            if(field.validator_fields) {
                                const obj = field.validator_fields.find(obj => obj.hasOwnProperty("NotEqualTo"));
                                if(obj) equal_fields = obj["NotEqualTo"];
                            }
                            val_object = val_object.notEqualTo(equal_fields, message);
                        }

                        if(field.min) {
                            message = ValidatorMessage(field, "Min", `Exceeded Minimum Characters: ${field.min}`);
                            val_object = val_object.minIfNotEmpty(field.min, message);
                        }
                        if(field.max && field.length) {
                            message = ValidatorMessage(field, "Max", `Exceeded Maximum Characters: ${field.max}`);
                            val_object = val_object.max(Math.min(field.max, field.length), message);
                        } else if (field.length) {
                            message = ValidatorMessage(field, "Max", `Exceeded Maximum Characters: ${field.max}`);
                            val_object = val_object.max(field.length, message);
                        }
                    }
                }
        }
        if(field.listFormat && !["Enum", "DataTable"].includes(field.type)) {
            val_object = Yup.array().ensure().of(val_object);

            required_if = RequiredIf(val_object, field, fields);
            if(required_if) {
                val_object = required_if;
            } else if(field.required) {
                message = ValidatorMessage(field, "Required", field.required_message);
                val_object = val_object.min(1, message);
            }

            if(field.listMin) {
                message = ValidatorMessage(field, "Min", message);
                val_object = val_object.min(field.listMin, message);
            }
            if(field.listMax) {
                message = ValidatorMessage(field, "Max", message);
                val_object = val_object.max(field.listMax, message);
            }
        }

        if(val_object) {
            set(schemas, field.name, val_object);
        }
    });
    // nested schemas
    const schema = flattenSchema(schemas);
    if(cyclic_fields) {
        // https://stackoverflow.com/questions/64020518/error-cyclic-dependency-with-yup-validation
        if(validation_schema) return validation_schema.shape(schema, cyclic_fields); // merge to existing schema
        return Yup.object().shape(schema, cyclic_fields);
    }

    if(validation_schema) return validation_schema.shape(schema); // merge to existing schema
    return Yup.object().shape(schema);
}

function flattenSchema(schemas) {
    // nested fieldnames ie: Params.maps.table
    return Object.entries(schemas).reduce((schema, prop) => {
        const [key, value] = prop;
        if(value.hasOwnProperty("type")) {
            // SchemaType - ie: table of Params.maps.table
            schema[key] = value;
        } else {
            // Object - create ObjectSchema - ie: Params.maps of Params.maps.table
            const scheme = flattenSchema(value);
            schema[key] = Yup.object().shape(scheme);
        }
        return schema;
    }, {});
}

Yup.addMethod(Yup.string, "minIfNotEmpty",
    function(min_value, message) {
        return this.test("minIfNotEmpty", message,
            function(value) {
                const { path, createError } = this;
                if(!isEmpty(value) && value.length < min_value) {
                    return createError({
                        path,
                        message: message || `${path} Minimum of ${min_value} characters`
                    });
                }
                return true;
            }
        );
    }
);

Yup.addMethod(Yup.string, "equalTo",
    function(refField, message) {
        return this.test("equalTo", message,
            function(value) {
                const { path, createError } = this;
                /**
                    Yup v0.32 (and earlier versions) doesn't preserve nested paths
                    like "Params.fromcompany" inside this.parent.
                    It only gives you the immediate parent object of the current field
                    — that would be the Params object.
                **/
                const equal_fields = refField.split('.').pop();  // fromcompany
                const otherValue = this.parent[equal_fields];
                if(value !== otherValue) {
                    return createError({
                        path,
                        message: message || `${path} is not equal to ${refField}`
                    });
                }
                return true;
            }
        );
    }
);

Yup.addMethod(Yup.string, "notEqualTo",
    function(refField, message) {
        return this.test("notEqualTo", message,
            function(value) {
                const { path, createError } = this;
                /**
                    Yup v0.32 (and earlier versions) doesn't preserve nested paths
                    like "Params.fromcompany" inside this.parent.
                    It only gives you the immediate parent object of the current field
                    — that would be the Params object.
                **/
                const equal_fields = refField.split('.').pop();  // fromcompany
                const otherValue = this.parent[equal_fields];
                if(value === otherValue) {
                    return createError({
                        path,
                        message: message || `${path} is equal to ${refField}`
                    });
                }
                return true;
            }
        );
    }
);

Yup.addMethod(Yup.number, "notZero",
    function(message) {
        return this.test("notZero", message,
            function(value) {
                const { path, createError } = this;
                if(value === 0) {
                    return createError({
                        path,
                        message: message || `${path} requires a non-zero value`
                    });
                }
                return true;
            }
        );
    }
);

Yup.addMethod(Yup.number, "zeroPositive",
    function(message) {
        return this.test("zeroPositive", message,
            function(value) {
                const { path, createError } = this;

                if(value < 0) {
                    return createError({
                        path,
                        message: message || `${path} requires a Zero or Positive value`
                    });
                }
                return true;
            }
        );
    }
);

Yup.addMethod(Yup.number, "negative",
    function(message) {
        return this.test("negative", message,
            function(value) {
                const { path, createError } = this;

                if(value >= 0) {
                    return createError({
                        path,
                        message: message || `${path} requires a Negative value`
                    });
                }
                return true;
            }
        );
    }
);

Yup.addMethod(Yup.number, "zeroNegative",
    function(message) {
        return this.test("zeroNegative", message,
            function(value) {
                const { path, createError } = this;

                if(value > 0) {
                    return createError({
                        path,
                        message: message || `${path} requires a Zero or Negative value`
                    });
                }
                return true;
            }
        );
    }
);

Yup.addMethod(Yup.number, "total",
    function(fields, message) {
        return this.test("total", message,
            function(value) {
                const { path, createError } = this;
                let sum_total = 0;
                for(const props in this.parent) {
                    let qty = 0
                    if(isArray(fields)) {
                        if(fields.includes(props)) {
                            if(!Number.isNaN(Number(this.parent[props]))) {
                                qty = Number(this.parent[props]);
                            }
                        }
                    } else if(props.startsWith(fields)) {
                        if(!Number.isNaN(Number(this.parent[props]))) {
                            qty = Number(this.parent[props]);
                        }
                    }
                    sum_total += qty
                }
                if(isNil(value)) {
                    value = 0;
                }
                if(value !== sum_total) {
                    return createError({
                        path,
                        message: message || `${path} not equal sum of ${fields}`
                    });
                }
                return true;
            }
        );
    }
);
