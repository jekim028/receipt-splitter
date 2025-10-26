/**
 * Receipt footer with totals
 */
import './ReceiptDisplay.css';

export const ReceiptFooter = ({ subtotal, tax, tip, total }) => {
  return (
    <div className="receipt-footer">
      <div className="footer-row">
        <span>SUBTOTAL:</span>
        <span>${subtotal?.toFixed(2) || '0.00'}</span>
      </div>
      <div className="footer-row">
        <span>TAX:</span>
        <span>${tax?.toFixed(2) || '0.00'}</span>
      </div>
      <div className="footer-row">
        <span>TIP:</span>
        <span>${tip?.toFixed(2) || '0.00'}</span>
      </div>
      <div className="footer-divider">- - - - - - - - - - - - - - - - -</div>
      <div className="footer-row total">
        <span>TOTAL:</span>
        <span>${total?.toFixed(2) || '0.00'}</span>
      </div>
    </div>
  );
};
