import { LitElement, html, css } from 'lit-element';
import { TWStyles } from '../css/tw.js'

// https://heroicons.com
// chevron-up
class ChevronUp extends LitElement {
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
                <path fill-rule="evenodd" d="M11.47 7.72a.75.75 0 0 1 1.06 0l7.5 7.5a.75.75 0 1 1-1.06 1.06L12 9.31l-6.97 6.97a.75.75 0 0 1-1.06-1.06l7.5-7.5Z" clip-rule="evenodd" />
            </svg>
        `;
    }
}

customElements.define('icon-chevronup', ChevronUp);
