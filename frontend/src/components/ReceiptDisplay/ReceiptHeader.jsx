/**
 * Receipt header component
 */
import './ReceiptDisplay.css';

export const ReceiptHeader = ({ establishment, date }) => {
  return (
    <div className="receipt-header">
      <div className="establishment">{establishment || 'RECEIPT'}</div>
      {date && <div className="date">{new Date(date).toLocaleString()}</div>}
    </div>
  );
};
