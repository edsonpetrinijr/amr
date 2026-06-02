import * as React from "react"
import { cn } from "./utils"

export interface BadgeProps extends React.HTMLAttributes<HTMLDivElement> {
  variant?: "default" | "success" | "destructive" | "outline" | "secondary"
}

function Badge({ className, variant = "default", ...props }: BadgeProps) {
  return (
    <div
      className={cn(
        "inline-flex items-center rounded-full border px-2.5 py-0.5 text-xs font-semibold transition-colors focus:outline-none focus:ring-2 focus:ring-gray-700 focus:ring-offset-2",
        {
          "border-transparent bg-[#1f6feb] text-white hover:bg-[#1f6feb]/80":
            variant === "default",
          "border-transparent bg-[#238636]/10 text-[#3fb950] border-[#2ea043]/30":
            variant === "success",
          "border-transparent bg-[#da3633]/10 text-[#ff7b72] border-[#f85149]/30":
            variant === "destructive",
          "border-transparent bg-[#30363d] text-[#c9d1d9] hover:bg-[#30363d]/80":
            variant === "secondary",
          "text-[#8b949e] border-[#30363d]": variant === "outline",
        },
        className
      )}
      {...props}
    />
  )
}

export { Badge }
