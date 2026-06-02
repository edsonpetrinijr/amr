import * as React from "react"
import { cn } from "./utils"

export interface ButtonProps
  extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "default" | "outline" | "ghost" | "primary"
  size?: "default" | "sm" | "lg" | "icon"
}

const Button = React.forwardRef<HTMLButtonElement, ButtonProps>(
  ({ className, variant = "default", size = "default", ...props }, ref) => {
    return (
      <button
        ref={ref}
        className={cn(
          "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gray-700 disabled:pointer-events-none disabled:opacity-50",
          {
            "bg-[#21262d] text-[#c9d1d9] hover:bg-[#30363d] border border-[#30363d]": variant === "default",
            "bg-[#238636] text-white hover:bg-[#2ea043]": variant === "primary",
            "border border-[#30363d] bg-transparent hover:bg-[#21262d] text-[#c9d1d9]": variant === "outline",
            "hover:bg-[#21262d] hover:text-[#c9d1d9] text-[#8b949e]": variant === "ghost",
            "h-9 px-4 py-2": size === "default",
            "h-8 rounded-md px-3 text-xs": size === "sm",
            "h-10 rounded-md px-8": size === "lg",
            "h-9 w-9": size === "icon",
          },
          className
        )}
        {...props}
      />
    )
  }
)
Button.displayName = "Button"

/** Class-string helper used by shadcn primitives (e.g. AlertDialog action/cancel)
 *  that style a plain element as a button. Mirrors the Button variants above. */
export function buttonVariants(opts?: { variant?: ButtonProps["variant"]; size?: ButtonProps["size"] }): string {
  const variant = opts?.variant ?? "default"
  const size = opts?.size ?? "default"
  return cn(
    "inline-flex items-center justify-center whitespace-nowrap rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-1 focus-visible:ring-gray-700 disabled:pointer-events-none disabled:opacity-50",
    {
      "bg-[#21262d] text-[#c9d1d9] hover:bg-[#30363d] border border-[#30363d]": variant === "default",
      "bg-[#238636] text-white hover:bg-[#2ea043]": variant === "primary",
      "border border-[#30363d] bg-transparent hover:bg-[#21262d] text-[#c9d1d9]": variant === "outline",
      "hover:bg-[#21262d] hover:text-[#c9d1d9] text-[#8b949e]": variant === "ghost",
      "h-9 px-4 py-2": size === "default",
      "h-8 rounded-md px-3 text-xs": size === "sm",
      "h-10 rounded-md px-8": size === "lg",
      "h-9 w-9": size === "icon",
    },
  )
}

export { Button }
