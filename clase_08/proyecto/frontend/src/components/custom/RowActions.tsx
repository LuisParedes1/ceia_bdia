import type { LucideIcon } from "lucide-react";
import { Button } from "../ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "../ui/tooltip";

export type RowAction = {
  label: string;
  icon: LucideIcon;
  onClick: () => void;
  disabled?: boolean;
  busy?: boolean;
  variant?: "default" | "ghost" | "outline";
};

export function RowActions({ actions }: { actions: RowAction[] }) {
  return (
    <TooltipProvider>
      <div className="row-actions">
        {actions.map(
          ({
            label,
            icon: Icon,
            onClick,
            disabled,
            busy,
            variant = "outline",
          }) => (
            <Tooltip key={label}>
              <TooltipTrigger>
                <Button
                  type="button"
                  variant={variant}
                  className="row-action-button"
                  aria-label={label}
                  disabled={disabled || busy}
                  aria-busy={busy || undefined}
                  onClick={onClick}
                >
                  <Icon />
                </Button>
              </TooltipTrigger>
              <TooltipContent>{label}</TooltipContent>
            </Tooltip>
          ),
        )}
      </div>
    </TooltipProvider>
  );
}
