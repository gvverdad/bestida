import { html, render } from 'lit'
import { unsafeHTML } from 'lit/directives/unsafe-html.js'

import api from "./api"
import { menu } from "./menu"
import breadcrumbs from "./breadcrumb"

import * as Yup from "yup";
import { navigateTo } from "./router";
import user from "./user";

// define globally - for template scripts
window.menu = menu;
window.api = api;
window.Yup = Yup;  // used in validation-schema functions
window.removeThisPage = breadcrumbs.remove_active_page;
window.resetApp = breadcrumbs.resetApp;
window.closePage = breadcrumbs.closePage;
window.navigateTo = navigateTo;
window.user = user;


class View {
    parseResponse(response_string, route) {
        const data = {
            title: "",
            html: "",
            script: ""
        };
        const doc = new DOMParser().parseFromString(response_string, 'text/html');

        const title = doc.querySelector('[data-title]');
        if(title) {
            data.title = title.getAttribute("data-title");
        } else {
            data.title = route.route.title;
        }

        const scriptTags = doc.querySelectorAll('script');
        scriptTags.forEach(function(scriptTag) {
            // Extract the content of the script tag
            data.script += scriptTag.textContent;
            // Remove the script tag from the doc
            scriptTag.parentNode.removeChild(scriptTag);
        });
        data.html = new XMLSerializer().serializeToString(doc);

        return data;
    }

    async getHtml(route) {
        const target = document.querySelector("[data-main_container]");
        try {
            await api.GET(route.result[0])
                .then(response => {
                    const data = this.parseResponse(response, route);
                    target.innerHTML = data.html;
                    if(data.script) {
                        const script = document.createElement("script");
                        script.textContent = data.script;
                        target.appendChild(script);
                    }
                    breadcrumbs.add(route, data);

                    // autofocus is not honoured in page nav - only on init load
                    const autofocusElement = document.querySelector('[autofocus]');
                    // Check if the autofocusElement exists and is not focused
                    if (autofocusElement && document.activeElement !== autofocusElement) {
                        autofocusElement.focus();
                    }
                });
        } catch (err) {
            const message = `view.getHtml ${err.status} ${err.detail} : ${route.route.title}`;
            const toaster = document.querySelector("[data-toaster]");
            toaster.show(message,"error");
        }
    }

    async submitForm(form) {
        const action = form.getAttribute("action");
        const method = form.getAttribute("method").toLowerCase();

        // Convert FormData to URL-encoded string
        const urlSearchParams = new URLSearchParams(new FormData(form));

        switch(method) {
            case "put":
                return api.PUT(action, urlSearchParams);
            case "delete":
                return api.DELETE(action, urlSearchParams);
            default:  // post
                return api.POST(action, urlSearchParams);
        }
    }
}

const view = new View();

export default view
