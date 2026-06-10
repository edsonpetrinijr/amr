import React from 'react'

interface PageHeaderProps {
  /** Optional leading icon (lucide node) shown before the title. */
  icon?: React.ReactNode
  /** Page title — uniform size on every page. */
  title: string
  /** Inline status content after the title (e.g. connection dot + stats span). */
  status?: React.ReactNode
  /** Right-aligned actions (buttons, toggles). */
  actions?: React.ReactNode
  /** Optional second row below the base bar (filter tabs / device tabs). */
  subBar?: React.ReactNode
}

/**
 * Uniform page header. The base title bar has a FIXED height (`min-h-[48px]`)
 * on every page so switching routes never shifts the content baseline. An
 * optional `subBar` renders a consistent secondary row below it.
 */
export function PageHeader({ icon, title, status, actions, subBar }: PageHeaderProps) {
  return (
    <>
      <div className="min-h-[48px] border-b border-[#30363d] px-6 flex items-center gap-3 flex-shrink-0">
        {icon}
        <h1 className="text-sm font-semibold text-[#e6edf3]">{title}</h1>
        {status}
        {actions && <div className="ml-auto flex items-center gap-2">{actions}</div>}
      </div>
      {subBar && (
        <div className="min-h-[40px] border-b border-[#30363d] px-4 flex items-center gap-1 flex-shrink-0 bg-[#0d1117]">
          {subBar}
        </div>
      )}
    </>
  )
}
