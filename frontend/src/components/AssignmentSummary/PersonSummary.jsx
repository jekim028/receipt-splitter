/**
 * Per-person summary component
 */
import './AssignmentSummary.css';

const PERSON_COLORS = [
  '#4f46e5', // blue
  '#10b981', // green
  '#f59e0b', // yellow
  '#ec4899', // pink
  '#8b5cf6', // purple
  '#3b82f6', // light blue
];

export const PersonSummary = ({ name, amount }) => {
  // Get consistent color for person
  const colorIndex = name.charCodeAt(0) % PERSON_COLORS.length;
  const color = PERSON_COLORS[colorIndex];

  return (
    <div className="person-summary">
      <div className="person-info">
        <div
          className="person-avatar"
          style={{ backgroundColor: color }}
        >
          {name.charAt(0).toUpperCase()}
        </div>
        <span className="person-name">{name}</span>
      </div>
      <div className="person-amount">${amount.toFixed(2)}</div>
    </div>
  );
};
