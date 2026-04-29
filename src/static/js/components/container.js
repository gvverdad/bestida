import { LitElement, html, css } from 'lit'
import { TWStyles } from '../../css/tw.js'

class Container extends LitElement {
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

    addElement(element) {
        const cont = this.shadowRoot.querySelector("[data-container]");
        // use removeChild loop instead of innerHTML = "" to properly
        // remove litelements
        while (cont.firstChild) {
            cont.removeChild(cont.firstChild);
        }
        cont.appendChild(element);
    }

    render() {
        return html`
            <div data-container></div>
        `;
    }
}

customElements.define("ui-container", Container)
