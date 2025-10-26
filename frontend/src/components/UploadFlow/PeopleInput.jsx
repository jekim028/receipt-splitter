/**
 * Component for inputting people names
 */
import { useState } from 'react';
import './PeopleInput.css';

export const PeopleInput = ({ onPeopleChange, onSubmit }) => {
  const [people, setPeople] = useState(['']);
  const [currentInput, setCurrentInput] = useState('');

  const addPerson = () => {
    if (currentInput.trim()) {
      const newPeople = [...people.filter(p => p.trim()), currentInput.trim()];
      setPeople([...newPeople, '']);
      setCurrentInput('');
      onPeopleChange?.(newPeople);
    }
  };

  const removePerson = (index) => {
    const newPeople = people.filter((_, i) => i !== index);
    setPeople(newPeople.length === 0 ? [''] : newPeople);
    onPeopleChange?.(newPeople.filter(p => p.trim()));
  };

  const handleKeyPress = (e) => {
    if (e.key === 'Enter') {
      e.preventDefault();
      addPerson();
    }
  };

  const handleSubmit = () => {
    const validPeople = people.filter(p => p.trim());
    if (validPeople.length >= 2) {
      onSubmit?.(validPeople);
    }
  };

  const validPeople = people.filter(p => p.trim());
  const canSubmit = validPeople.length >= 2;

  return (
    <div className="people-input">
      <h3>Who's splitting?</h3>
      <p className="subtitle">Add at least 2 people</p>

      <div className="people-list">
        {people.map((person, index) => (
          <div key={index} className="person-row">
            {person ? (
              <div className="person-chip">
                <span className="person-name">{person}</span>
                <button
                  className="remove-button"
                  onClick={() => removePerson(index)}
                  aria-label="Remove person"
                >
                  ×
                </button>
              </div>
            ) : (
              <div className="input-container">
                <input
                  type="text"
                  value={currentInput}
                  onChange={(e) => setCurrentInput(e.target.value)}
                  onKeyPress={handleKeyPress}
                  placeholder="Enter name..."
                  className="name-input"
                  autoFocus
                />
                <button
                  className="add-button"
                  onClick={addPerson}
                  disabled={!currentInput.trim()}
                >
                  Add
                </button>
              </div>
            )}
          </div>
        ))}
      </div>

      {validPeople.length > 0 && validPeople.length < 2 && (
        <p className="hint">Add at least one more person</p>
      )}

      <button
        className="submit-button"
        onClick={handleSubmit}
        disabled={!canSubmit}
      >
        Start Splitting ({validPeople.length} {validPeople.length === 1 ? 'person' : 'people'})
      </button>
    </div>
  );
};
