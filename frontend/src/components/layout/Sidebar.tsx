"use client";

import { useRouter, usePathname } from 'next/navigation';
import type { Route } from 'next';
import { cn } from '@/lib/utils';
import {
  LayoutDashboard,
  ListTodo,
  Settings,
  ChevronLeft,
  ChevronRight,
  User,
} from 'lucide-react';
import type { LucideIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { motion } from 'framer-motion';

interface SidebarProps {
  isOpen: boolean;
  onToggle: () => void;
}

type NavigationItem = {
  name: string;
  href: Route;
  icon: LucideIcon;
};

const navigation: NavigationItem[] = [
  {
    name: 'Dashboard',
    href: '/dashboard',
    icon: LayoutDashboard,
  },
  {
    name: 'Tasks',
    href: '/tasks',
    icon: ListTodo,
  },
  {
    name: 'Profile',
    href: '/profile',
    icon: User,
  },
  {
    name: 'Settings',
    href: '/settings',
    icon: Settings,
  },
];

export function Sidebar({ isOpen, onToggle }: SidebarProps) {
  const router = useRouter();
  const pathname = usePathname();

  return (
    <motion.div
      initial={false}
      animate={{ width: isOpen ? 200 : 64 }}
      className="bg-card/80 dark:bg-card/80 backdrop-blur-xl border-r border-border flex flex-col min-h-0 overflow-hidden shadow-xl shadow-gray-900/10 transition-all duration-300"
    >
      {/* Header */}
      <div className="p-4 border-b border-border">
        <div className="flex items-center justify-between">
          {isOpen && (
            <motion.h1
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="text-xl font-bold"
            >
              PrioritiAI
            </motion.h1>
          )}
          <Button
            variant="ghost"
            size="sm"
            onClick={onToggle}
            className="ml-auto"
          >
            {isOpen ? <ChevronLeft className="h-4 w-4" /> : <ChevronRight className="h-4 w-4" />}
          </Button>
        </div>
      </div>

      {/* Navigation */}
      <nav className="flex-1 p-4 space-y-2 min-h-0 overflow-auto relative z-50">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Button
              key={item.name}
              variant={isActive ? "default" : "ghost"}
              className={cn(
                "w-full justify-start relative z-50",
                !isOpen && "px-2"
              )}
              onClick={() => router.push(item.href)}
            >
              <item.icon className={cn("h-4 w-4", isOpen && "mr-2")} />
              {isOpen && <span>{item.name}</span>}
            </Button>
          );
        })}
      </nav>
    </motion.div>
  );
}
