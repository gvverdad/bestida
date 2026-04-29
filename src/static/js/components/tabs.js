import { LitElement, html, css } from 'lit'
import { unsafeHTML } from 'lit/directives/unsafe-html.js';
import { TWStyles } from '../../css/tw.js'

import { isNull, isEmpty } from "../utils"

class Tabs extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static properties = {
        ownerId: { attribute: "owner-id", type: String },
        selectedTabIndex: { attribute: "selected-index", type: Number },

        tabElements: { state: true }
    };

    constructor() {
        super();

        this.selectedTabIndex = 0;
        this.tabElements = [];
    }

    firstUpdated() {
        this.tabElements = Array.from(this.children);
        this.showTabContent();
    }

    selectTab(index) {
        this.selectedTabIndex = index;
        this.showTabContent();

        this.dispatchEvent(new CustomEvent(`tab-select-${this.ownerId}`, {
            bubbles: true,
            composed: true,
            detail: {
                value: index,
                url: this.tabElements[this.selectedTabIndex].url
            }
        }));
    }

    showTabContent() {
        if(this.tabElements[this.selectedTabIndex].url) {
            this.tabElements[this.selectedTabIndex].showContent();
        }
    }

    render() {
        if(isEmpty(this.tabElements)) return;

        return html`
            <div class="card w-full bg-base-100 shadow-xl overflow-y-auto">
                <div class="navbar bg-base-200 flex justify-between items-center">
                    <div class="tabs">
                        ${this.tabElements.map((child, index) => html`
                            <a class="${index === this.selectedTabIndex ? 'tab tab-bordered tab-active text-sm font-semibold' : 'tab tab-bordered text-sm font-semibold'}"
                                @click=${() => this.selectTab(index)}>
                                ${child.getAttribute('tab-title')}
                            </a>
                        `)}
                    </div>
                </div>
                <div class="card-body" style="padding-top: 5px; padding-bottom: 10px;">
                    ${this.tabElements[this.selectedTabIndex]}
                </div>
            </div>
        `;
    }
}
customElements.define("ui-tabs", Tabs)


class Tab extends LitElement {
    static properties = {
        title: { attribute: "tab-title", type: String },
        url: { type: String },

        content: { state: true }
    };

    constructor() {
        super();

        this.title = "Tab Title";
        this.url = null;
        this.content = null;
    }

    async showContent() {
        if(isNull(this.url)) return false;

        await fetch(this.url)
            .then((response) => response.text())
            .then((html) => {
                this.content = html;
            })
            .catch((error) => {
                console.error(`Error loading tab content: ${error} : ${this.title} : ${this.url}`);
            });
    }

    render() {
        return html`
            <slot ?hidden=${this.url}></slot>
            ${unsafeHTML(this.content)}
        `;
    }
}
customElements.define("ui-tab", Tab)
