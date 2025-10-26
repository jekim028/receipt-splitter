/**
 * Individual receipt item component
 */
import './ReceiptDisplay.css';

const PERSON_COLORS = [
  '#eef2ff', // blue
  '#f0fdf4', // green
  '#fef3c7', // yellow
  '#fce7f3', // pink
  '#f3e8ff', // purple
  '#dbeafe', // light blue
];

export const ReceiptItem = ({ item, assignment, isHighlighted }) => {
  const assignedTo = assignment?.assigned_to || [];
  const hasAssignment = assignedTo.length > 0;

  // Get color based on first assigned person (for consistent coloring)
  const getBackgroundColor = () => {
    if (!hasAssignment) return 'transparent';
    // Use first person's index for color consistency
    const colorIndex = assignedTo[0].charCodeAt(0) % PERSON_COLORS.length;
    return PERSON_COLORS[colorIndex];
  };

  return (
    <div
      className={`receipt-item ${isHighlighted ? 'highlighted' : ''} ${!hasAssignment ? 'unassigned' : ''}`}
      style={{ backgroundColor: getBackgroundColor() }}
    >
      <div className="item-row">
        <span className="item-line">{item.line_number}.</span>
        <span className="item-desc">{item.desc_clean || item.description}</span>
        <span className="item-price">${item.line_total?.toFixed(2) || '0.00'}</span>
      </div>
      {hasAssignment && (
        <div className="item-assignment">
          <span className="assignment-label">→</span>
          <span className="assignment-people">{assignedTo.join(', ')}</span>
          {assignment.split_strategy !== 'equal' && (
            <span className="assignment-strategy">({assignment.split_strategy})</span>
          )}
        </div>
      )}
    </div>
  );
};
