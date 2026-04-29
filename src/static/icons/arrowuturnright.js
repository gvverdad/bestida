import { LitElement, html, css } from 'lit-element';
import { TWStyles } from '../css/tw.js'

// https://heroicons.com
// arrow uturn right
class ArrowUturnRight extends LitElement {
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
                <path fill-rule="evenodd" d="M14.47 2.47a.75.75 0 0 1 1.06 0l6 6a.75.75 0 0 1 0 1.06l-6 6a.75.75 0 1 1-1.06-1.06l4.72-4.72H9a5.25 5.25 0 1 0 0 10.5h3a.75.75 0 0 1 0 1.5H9a6.75 6.75 0 0 1 0-13.5h10.19l-4.72-4.72a.75.75 0 0 1 0-1.06Z" clip-rule="evenodd" />
            </svg>
        `;
    }
}

customElements.define('icon-arrowuturnright', ArrowUturnRight);
