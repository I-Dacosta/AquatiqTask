'use client'

import * as React from 'react'
import Link from 'next/link'
import type { Route } from 'next'
import { usePathname } from 'next/navigation'
import { cn } from '@/lib/utils'
import { Button } from '@/components/ui/button'
import {
  NavigationMenu,
  NavigationMenuContent,
  NavigationMenuItem,
  NavigationMenuLink,
  NavigationMenuList,
  NavigationMenuTrigger,
} from '@/components/ui/navigation-menu'
import { 
  Home, 
  BarChart3, 
  Settings, 
  User, 
  Plus,
  Search,
  Command
} from 'lucide-react'
import type { LucideIcon } from 'lucide-react'

type NavigationItem = {
  name: string
  href: Route
  icon: LucideIcon
  description: string
}

const navigation: NavigationItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: BarChart3,
    description: 'Overview of your activity and analytics',
  },
  {
    name: 'Tasks',
    href: '/tasks',
    icon: Home,
    description: 'Manage and prioritize your tasks',
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
    description: 'Configure your preferences',
  },
  {
    name: 'Profile',
    href: '/profile',
    icon: User,
    description: 'View and edit your profile',
  },
]

export function MainNav() {
  const pathname = usePathname()

  return (
    <div className="mr-4 hidden md:flex">
      <Link href="/dashboard" className="mr-6 flex items-center space-x-2">
        <BarChart3 className="h-6 w-6" />
        <span className="hidden font-bold sm:inline-block">
          PrioritiAI
        </span>
      </Link>
      <NavigationMenu>
        <NavigationMenuList>
          {navigation.map((item) => (
            <NavigationMenuItem key={item.name}>
              <NavigationMenuLink asChild>
                <Link
                  href={item.href}
                  className={cn(
                    'group inline-flex h-9 w-max items-center justify-center rounded-md bg-background px-4 py-2 text-sm font-medium transition-colors hover:bg-accent hover:text-accent-foreground focus:bg-accent focus:text-accent-foreground focus:outline-none disabled:pointer-events-none disabled:opacity-50 data-[active]:bg-accent/50 data-[state=open]:bg-accent/50',
                    pathname === item.href && 'bg-accent text-accent-foreground'
                  )}
                >
                  <item.icon className="mr-2 h-4 w-4" />
                  {item.name}
                </Link>
              </NavigationMenuLink>
            </NavigationMenuItem>
          ))}
        </NavigationMenuList>
      </NavigationMenu>
    </div>
  )
}

export function MobileNav() {
  const [open, setOpen] = React.useState(false)
  const pathname = usePathname()

  return (
    <div className="flex md:hidden">
      <Button
        variant="ghost"
        className="mr-2 px-0 text-base hover:bg-transparent focus-visible:bg-transparent focus-visible:ring-0 focus-visible:ring-offset-0"
        onClick={() => setOpen(!open)}
      >
        <Command className="h-5 w-5" />
        <span className="sr-only">Toggle Menu</span>
      </Button>
      {open && (
        <div className="fixed inset-0 top-16 z-50 grid h-[calc(100vh-4rem)] w-full grid-flow-row auto-rows-max overflow-auto p-6 pb-32 shadow-md animate-in slide-in-from-bottom-80 md:hidden">
          <div className="relative z-20 grid gap-6 rounded-md bg-popover p-4 text-popover-foreground shadow-md">
            <Link href="/dashboard" className="flex items-center space-x-2">
              <BarChart3 className="h-6 w-6" />
              <span className="font-bold">PrioritiAI</span>
            </Link>
            <nav className="grid grid-flow-row auto-rows-max text-sm">
              {navigation.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className={cn(
                    'flex w-full items-center rounded-md p-2 text-sm font-medium hover:underline',
                    pathname === item.href ? 'text-foreground' : 'text-foreground/60'
                  )}
                  onClick={() => setOpen(false)}
                >
                  <item.icon className="mr-2 h-4 w-4" />
                  {item.name}
                </Link>
              ))}
            </nav>
          </div>
        </div>
      )}
    </div>
  )
}