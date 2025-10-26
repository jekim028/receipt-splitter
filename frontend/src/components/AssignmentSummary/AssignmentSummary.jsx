/**
 * Assignment summary showing per-person breakdown
 */
import { PersonSummary } from './PersonSummary';
import './AssignmentSummary.css';

export const AssignmentSummary = ({ totals, people, unassignedCount, onConfirm }) => {
  const totalAssigned = Object.values(totals).reduce((sum, amount) => sum + amount, 0);
  const allAssigned = unassignedCount === 0;

  return (
    <div className="assignment-summary">
      <div className="summary-header">
        <h3>Split Summary</h3>
        {unassignedCount > 0 && (
          <div className="unassigned-badge">
            {unassignedCount} item{unassignedCount !== 1 ? 's' : ''} unassigned
          </div>
        )}
      </div>

      <div className="people-summaries">
        {people.map((person) => (
          <PersonSummary
            key={person}
            name={person}
            amount={totals[person] || 0}
          />
        ))}
      </div>

      <div className="summary-total">
        <span>Total Split:</span>
        <span className="total-amount">${totalAssigned.toFixed(2)}</span>
      </div>

      {onConfirm && (
        <button
          className="confirm-button"
          onClick={onConfirm}
          disabled={!allAssigned}
        >
          {allAssigned ? 'Confirm Split' : 'Assign All Items First'}
        </button>
      )}

      {!allAssigned && (
        <p className="hint">
          All items must be assigned before confirming the split
        </p>
      )}
    </div>
  );
};
