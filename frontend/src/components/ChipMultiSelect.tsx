import { useState } from "react";

interface ChipMultiSelectProps {
  options: string[];
  selected: string[];
  onChange: (selected: string[]) => void;
  allowCustom?: boolean;
  placeholder?: string;
}

export function ChipMultiSelect({
  options,
  selected,
  onChange,
  allowCustom = false,
  placeholder = "Type and press Enter to add",
}: ChipMultiSelectProps) {
  const [customInput, setCustomInput] = useState("");

  function toggleOption(option: string) {
    if (selected.includes(option)) {
      onChange(selected.filter((s) => s !== option));
    } else {
      onChange([...selected, option]);
    }
  }

  function addCustom() {
    const trimmed = customInput.trim();
    if (trimmed && !selected.includes(trimmed)) {
      onChange([...selected, trimmed]);
    }
    setCustomInput("");
  }

  function handleKeyDown(e: React.KeyboardEvent<HTMLInputElement>) {
    if (e.key === "Enter") {
      e.preventDefault();
      addCustom();
    }
  }

  function removeSelected(item: string) {
    onChange(selected.filter((s) => s !== item));
  }

  const customSelected = selected.filter((s) => !options.includes(s));

  return (
    <div className="chip-multiselect">
      <div className="chip-options">
        {options.map((option) => (
          <button
            key={option}
            type="button"
            className={`chip ${selected.includes(option) ? "chip-selected" : ""}`}
            onClick={() => toggleOption(option)}
          >
            {option}
          </button>
        ))}
      </div>

      {allowCustom && (
        <div className="chip-custom-input">
          <input
            type="text"
            value={customInput}
            onChange={(e) => setCustomInput(e.target.value)}
            onKeyDown={handleKeyDown}
            placeholder={placeholder}
          />
          <button type="button" onClick={addCustom}>
            Add
          </button>
        </div>
      )}

      {customSelected.length > 0 && (
        <div className="chip-custom-selected">
          {customSelected.map((item) => (
            <span key={item} className="chip chip-selected">
              {item}
              <button type="button" onClick={() => removeSelected(item)}>
                ×
              </button>
            </span>
          ))}
        </div>
      )}
    </div>
  );
}