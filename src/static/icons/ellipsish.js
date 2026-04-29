import { LitElement, html, css } from 'lit-element';
import { TWStyles } from '../css/tw.js'

// https://heroicons.com
// ellipsis horizontal
class EllipsisH extends LitElement {
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
                <path fill-rule="evenodd" d="M4.5 12a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Zm6 0a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Zm6 0a1.5 1.5 0 1 1 3 0 1.5 1.5 0 0 1-3 0Z" clip-rule="evenodd" />
            </svg>
        `;
    }
}

customElements.define('icon-ellipsish', EllipsisH);
