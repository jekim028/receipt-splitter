/**
 * Main receipt display component with thermal receipt styling
 */
import { ReceiptHeader } from './ReceiptHeader';
import { ReceiptItem } from './ReceiptItem';
import { ReceiptFooter } from './ReceiptFooter';
import './ReceiptDisplay.css';

export const ReceiptDisplay = ({ receipt, assignments, highlightedItems = [] }) => {
  if (!receipt) {
    return (
      <div className="receipt-container">
        <div className="receipt-empty">No receipt loaded</div>
      </div>
    );
  }

  return (
    <div className="receipt-container">
      <div className="receipt-paper">
        <ReceiptHeader
          establishment={receipt.establishment}
          date={receipt.date}
        />

        <div className="receipt-divider">- - - - - - - - - - - - - - - - -</div>

        <div className="receipt-items">
          {receipt.line_items && receipt.line_items.map((item) => {
            const assignment = assignments?.[item.id];
            const isHighlighted = highlightedItems.includes(item.id);

            return (
              <ReceiptItem
                key={item.id}
                item={item}
                assignment={assignment}
                isHighlighted={isHighlighted}
              />
            );
          })}
        </div>

        <div className="receipt-divider">- - - - - - - - - - - - - - - - -</div>

        <ReceiptFooter
          subtotal={receipt.subtotal}
          tax={receipt.tax}
          tip={receipt.tip}
          total={receipt.total}
        />
      </div>
    </div>
  );
};
