import React, { useState, useRef, useEffect } from 'react';

interface SelectProps {
  value: string;
  onValueChange: (value: string) => void;
  children: React.ReactNode;
}

interface SelectTriggerProps {
  children: React.ReactNode;
  className?: string;
}

interface SelectContentProps {
  children: React.ReactNode;
}

interface SelectItemProps {
  value: string;
  children: React.ReactNode;
}

interface SelectValueProps {
  placeholder?: string;
}

export const Select: React.FC<SelectProps> = ({ value, onValueChange, children }) => {
  const [isOpen, setIsOpen] = useState(false);
  const selectRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (selectRef.current && !selectRef.current.contains(event.target as Node)) {
        setIsOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <div ref={selectRef} className="select-container">
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child)) {
          if (child.type === SelectTrigger) {
            return React.cloneElement(child, {
              onClick: () => setIsOpen(!isOpen),
              isOpen
            } as any);
          }
          if (child.type === SelectContent) {
            return isOpen ? React.cloneElement(child, {
              onSelect: (selectedValue: string) => {
                onValueChange(selectedValue);
                setIsOpen(false);
              },
              currentValue: value
            } as any) : null;
          }
        }
        return child;
      })}
    </div>
  );
};

export const SelectTrigger: React.FC<SelectTriggerProps & { onClick?: () => void; isOpen?: boolean }> = ({
  children,
  className = '',
  onClick,
  isOpen
}) => {
  return (
    <button
      type="button"
      onClick={onClick}
      className={`select-trigger ${className} ${isOpen ? 'open' : ''}`}
    >
      {children}
      <svg
        className={`select-arrow ${isOpen ? 'rotate' : ''}`}
        width="12"
        height="12"
        viewBox="0 0 12 12"
        fill="none"
      >
        <path
          d="M3 4.5L6 7.5L9 4.5"
          stroke="currentColor"
          strokeWidth="1.5"
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </svg>
    </button>
  );
};

export const SelectContent: React.FC<SelectContentProps & { onSelect?: (value: string) => void; currentValue?: string }> = ({
  children,
  onSelect,
  currentValue
}) => {
  return (
    <div className="select-content">
      {React.Children.map(children, (child) => {
        if (React.isValidElement(child) && child.type === SelectItem) {
          return React.cloneElement(child, {
            onSelect,
            isSelected: child.props.value === currentValue
          } as any);
        }
        return child;
      })}
    </div>
  );
};

export const SelectItem: React.FC<SelectItemProps & { onSelect?: (value: string) => void; isSelected?: boolean }> = ({
  value,
  children,
  onSelect,
  isSelected
}) => {
  return (
    <button
      type="button"
      onClick={() => onSelect?.(value)}
      className={`select-item ${isSelected ? 'selected' : ''}`}
    >
      {children}
    </button>
  );
};

export const SelectValue: React.FC<SelectValueProps> = ({ placeholder }) => {
  return <span className="select-value">{placeholder}</span>;
};