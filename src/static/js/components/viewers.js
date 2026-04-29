import { LitElement, html, css, nothing } from 'lit'
import { TWStyles } from '../../css/tw.js'

import { isEmpty } from "../utils"


class PDFViewer extends LitElement {
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

    static properties = {
        file: { type: String},
    }

    constructor() {
        super();

        this.file = null;
    }

    firstUpdated() {
        const element = this.shadowRoot.querySelector("[data-container]");
        // TODO: fix flicker
        const iframe = document.createElement('iframe');
        iframe.src = `/static/3rd/js/pdfjs-2.5.207-dist/web/viewer.html?file=${this.file}`;
        iframe.width = '100%';
        iframe.height = '100%';

        element.appendChild(iframe);
    }

    shouldUpdate(changedProperties) {
        // check if can render

        if(isEmpty(this.file)) return false;
        return true;
    }

    render() {
        return html`
            <div data-container
                class="h-full w-full"></div>
        `;
    }

}
customElements.define("pdf-viewer", PDFViewer)

class FileViewer extends LitElement {
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

    static properties = {
        title: { attribute: "file-title", type: String},
        file: { type: String},
        fileName: { attribute: "file-name", type: String},
        fileExt: { attribute: "file-ext", type: String},
    }

    constructor() {
        super();

        this.title = null;
        this.file = null;
        this.fileName = null;
        this.fileExt = null;
    }

    connectedCallback() {
        super.connectedCallback();

    }

    shouldUpdate(changedProperties) {
        // check if can render

        if(isEmpty(this.file)) return false;
        return true;
    }

    render() {
        if(this.fileExt === ".pdf") {
            return html`
                <pdf-viewer
                    file="${this.file}"
                ></pdf-viewer>
            `;
        }
        return html`
            <div>${this.fileExt} not yet supported</div>
        `;
    }
}
customElements.define("ui-fileviewer", FileViewer)


class ImageViewer extends LitElement {
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

    static properties = {
        title: { attribute: "image-title", type: String},
        section: { type: String},
        description: { type: String},
        footnote: { type: String},
        file: { type: String},
    }

    constructor() {
        super();

        this.title = null;
        this.section = null;
        this.description = null;
        this.footnote = null;
        this.file = null;
    }

    connectedCallback() {
        super.connectedCallback();

    }

    shouldUpdate(changedProperties) {
        // check if can render
        if(isEmpty(this.file)) return false;
        return true;
    }

    render() {
        return html`
            <div class="flex justify-center px-2 sm:px-4">
                <div class="card card-hover bg-base-100 shadow-xl inline-flex w-fit mx-auto my-4">
                    <div class="card-body items-center text-center gap-1 sm:gap-2 p-3 sm:p-4">
                        <img
                            src=${this.file}
                            loading="lazy"
                            alt="Product"
                            class="
                                rounded-lg
                                object-contain
                                w-full max-w-[400px]
                                sm:w-[400px] sm:h-[400px]
                            "
                        />
                        ${this.title ?
                            html`<h2 class="card-title text-sm sm:text-base">
                                ${this.title}
                            </h2>`
                        : nothing}

                        ${this.section ?
                            html`<p class="text-xs sm:text-sm font-medium text-base-content/80">
                                ${this.section}
                            </p>`
                        : nothing}

                        ${this.description ?
                            html`<p class="text-[11px] sm:text-xs text-base-content/60">
                                ${this.description}
                            </p>`
                        : nothing}

                        ${this.footnote ?
                            html`<p class="text-[10px] sm:text-[11px] md:text-xs text-base-content/40">
                                ${this.footnote}
                            </p>`
                        : nothing}
                    </div>
                </div>
            </div>
        `;
    }
}
customElements.define("ui-imageviewer", ImageViewer)
