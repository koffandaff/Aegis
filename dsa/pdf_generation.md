# PDF Generation Algorithm: Recursive Canvas Slicing

## Overview
We generate multi-page PDFs from HTML content (like security scan reports) using a helper function `addMultiPageContent` in `frontend/js/utils.js` (and various view files). The core challenge is rendering dynamic, long HTML content onto fixed-size A4 PDF pages without cutting text or images awkwardly.

## Algorithm Description
The algorithm uses a **Divide and Conquer** strategy combined with **Linear Scanning**:

1.  **Capture:** We capture the entire HTML element as a single large image (Canvas) using `html2canvas`.
2.  **Dimension Calculation:** We determine the A4 page height in pixels relative to the canvas width.
3.  **Recursion / Iteration:**
    *   Initialize `heightLeft` = Total Content Height.
    *   Initialize `position` = 0.
    *   **While** `heightLeft > 0`:
        *   Create a clean page in the PDF document (`doc.addPage()`).
        *   **Slice** the source canvas: We take a slice of the image from `position` to `position + pageHeight`.
        *   **Draw** this slice onto the PDF page.
        *   Update `heightLeft` -= `pageHeight`.
        *   Update `position` += `pageHeight`.
4.  **Save:** Once all slices are draw, save the PDF.

## Implementation in Fsociety
(Simplified logic from `frontend/js/views/scan.js`)

```javascript
// A4 Dimensions: 210mm x 297mm
const imgWidth = 210; 
const pageHeight = 295; 
const imgHeight = (canvas.height * imgWidth) / canvas.width;
let heightLeft = imgHeight;
let position = 0;

// First Page
doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
heightLeft -= pageHeight;

// Subsequent Pages (Loop)
while (heightLeft >= 0) {
    position = heightLeft - imgHeight; // Calculate offset
    doc.addPage();
    doc.addImage(imgData, 'PNG', 0, position, imgWidth, imgHeight);
    heightLeft -= pageHeight;
}
```
*Note: Our actual implementation improved on this by adding margins and headers/footers recursively.*

### Why we used this algorithm
*   **Fidelity:** It preserves the exact look of the HTML (CSS, Fonts, Charts) because it captures pixels.
*   **Reliability:** Native PDF generation from raw text/HTML is often buggy with complex CSS (Flexbox/Grid). Image slicing guarantees WYSIWYG results.
*   **Efficiency:** `html2canvas` handles the heavy lifting of rendering; we just manage the layout.

## Similar Interview Questions
1.  **Question:** How would you implement a "Print Preview" that splits content into pages?
    *   **Answer:** I would traverse the DOM tree. For each element, check `element.offsetTop + element.offsetHeight`. If it crosses a page boundary, insert a "page break" element or push the element to the next page.
2.  **Question:** Explain the trade-offs between Rasterization (Canvas) vs. Vector (Native PDF) generation.
    *   **Answer:** Rasterization (our approach) is pixel-perfect but text is not selectable/searchable and file size is larger. Vector (Native) is searchable and small but hard to style perfectly.

