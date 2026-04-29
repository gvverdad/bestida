import { LitElement, html, css } from 'lit-element';
import { TWStyles } from '../css/tw.js'

// https://heroicons.com
// plus
class Plus extends LitElement {
    static styles = [
        css `
            :host{
                display: block;
            }
        `,
        TWStyles
    ];

    static properties = {
        class: { type: String },
    };

    constructor() {
        super();
        this.class = "w-6 h-6";
    }

    render() {
        return html`
            <svg class="${this.class}"
                xmlns="http://www.w3.org/2000/svg" viewBox="0 0 24 24" fill="currentColor">
                <path fill-rule="evenodd" d="M12 3.75a.75.75 0 0 1 .75.75v6.75h6.75a.75.75 0 0 1 0 1.5h-6.75v6.75a.75.75 0 0 1-1.5 0v-6.75H4.5a.75.75 0 0 1 0-1.5h6.75V4.5a.75.75 0 0 1 .75-.75Z" clip-rule="evenodd" />
            </svg>
        `;
    }
}

customElements.define('icon-plus', Plus);
