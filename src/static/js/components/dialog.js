import { LitElement, html, css } from 'lit'
import { TWStyles } from '../../css/tw.js'


class Dialog extends LitElement {
    static styles = [
        css `
        `,
        TWStyles
    ];

    static properties = {
        ownerId: { attribute: "owner-id", type: String }
    };

    handleClose(event) {
        this.dispatchEvent(new CustomEvent(`dialog-close-${this.ownerId}`, {
            bubbles: true,
            composed: true,
        }));
    }

    showModal() {
        // handle click outside
        const dialog = this.shadowRoot.querySelector("dialog");
        dialog.addEventListener('click', () => dialog.close());
        const box = this.shadowRoot.querySelector(".modal-box");
        box.addEventListener('click', (event) => event.stopPropagation());
        dialog.showModal();
    }

    closeModal() {
        const dialog = this.shadowRoot.querySelector("dialog");
        dialog.close();
    }

    render() {
        return html`
            <dialog class="modal" @close="${this.handleClose}">
                <div class="modal-box w-fit">
                    <slot></slot>
                </div>
            </dialog>
        `;
    }
}

customElements.define("ui-dialog", Dialog)
