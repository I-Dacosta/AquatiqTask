"use client"

import * as React from 'react'
import { cn } from '@/lib/utils'

type HoverBorderGradientProps = React.ButtonHTMLAttributes<HTMLButtonElement> & {
	as?: React.ElementType
}

const HoverBorderGradient = React.forwardRef<HTMLButtonElement, HoverBorderGradientProps>(
	({ as, className, children, ...props }, ref) => {
		const Component = (as ?? 'button') as React.ElementType

		return (
			<Component
				ref={ref as React.Ref<HTMLElement>}
				className={cn(
					'group relative inline-flex items-center justify-center overflow-hidden rounded-md transition-all focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring/50 focus-visible:ring-offset-2',
					className
				)}
				{...props}
			>
				<span className="absolute inset-0 rounded-md bg-gradient-to-r from-primary/0 via-primary/60 to-primary/0 opacity-0 transition-opacity duration-300 group-hover:opacity-100" />
				<span className="relative z-10">{children}</span>
			</Component>
		)
	}
)

HoverBorderGradient.displayName = 'HoverBorderGradient'

export { HoverBorderGradient }
