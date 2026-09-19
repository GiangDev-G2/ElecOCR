interface StatusBadgeProps {
  tone: "neutral" | "success" | "warning" | "error";
  children: string;
}

export function StatusBadge({ tone, children }: StatusBadgeProps) {
  return (
    <span className={`status-badge status-badge--${tone}`}>
      <span className="status-badge__dot" aria-hidden="true" />
      {children}
    </span>
  );
}
