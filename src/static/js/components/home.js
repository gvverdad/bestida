import { LitElement, html, css, nothing } from 'lit'
import { classMap } from 'lit/directives/class-map.js';
import { TWStyles } from '../../css/tw.js'

import api from "../api"
import svg from "../svg"

class Home extends LitElement {
    static styles = [
        css `
            :host{
                height: 100%;
                width: 100%;
                overflow: auto;
            }
        `,
        TWStyles
    ];

    static instanceCounter = 0;

    static properties = {
        bookmarks: { type: Array },
        tabSelect: { attribute: "tab-select", type: Number },
    };

    constructor() {
        super();
        this.instanceId = "Home-" + (++Home.instanceCounter).toString();

        this.handleTabSelect = this.handleTabSelect.bind(this);

        this.bookmarks = [];
        this.tabSelect = 0;

        this.addEventListener(`tab-select-${this.instanceId}`, this.handleTabSelect);
    }

    connectedCallback() {
        super.connectedCallback();
    }

    handleTabSelect(event) {
        // bubbled up event from tabs
        this.tabSelect = event.detail.value;
        api.POST("/updateHomeActivePage", new URLSearchParams("active_page="+event.detail.url));
    }

    render() {
        return html`
            <div class="block w-full h-full overflow-auto">
                <slot ?hidden=${this.bookmarks.length}></slot>
                ${this.bookmarks.length ?
                    html `
                    <ui-tabs owner-id="${this.instanceId}" selected-index="${this.tabSelect}">
                    ${this.bookmarks.map((item) =>
                        html `
                            <ui-tab tab-title="${item.title}"
                                url="${item.url}">
                            </ui-tab>
                        `
                    )}
                    </ui-tabs>
                    `
                : nothing }
            </div>
        `
    }
}
customElements.define("ui-home", Home)
