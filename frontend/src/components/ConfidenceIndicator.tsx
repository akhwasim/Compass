interface ConfidenceIndicatorProps {
  level: string;
}

const ROTATION: Record<string, number> = {
  high: 45,
  medium: 0,
  low: -45,
};

export function ConfidenceIndicator({ level }: ConfidenceIndicatorProps) {
  const key = level.toLowerCase();
  const rotation = ROTATION[key] ?? 0;

  return (
    <span className={`confidence-badge confidence-${key}`}>
      <svg viewBox="0 0 24 24" fill="none">
        <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="1.3" />
        <line
          x1="12"
          y1="12"
          x2="12"
          y2="4"
          stroke="currentColor"
          strokeWidth="1.6"
          strokeLinecap="round"
          transform={`rotate(${rotation} 12 12)`}
        />
        <circle cx="12" cy="12" r="1.4" fill="currentColor" />
      </svg>
      {level}
    </span>
  );
}