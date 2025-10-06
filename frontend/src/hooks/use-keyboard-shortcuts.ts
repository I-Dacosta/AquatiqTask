'use client'

import { useEffect, useCallback } from 'react'

interface KeyboardShortcut {
  key: string
  ctrlKey?: boolean
  metaKey?: boolean
  shiftKey?: boolean
  altKey?: boolean
  action: () => void
  description?: string
}

export function useKeyboardShortcuts(shortcuts: KeyboardShortcut[]) {
  const handleKeyDown = useCallback(
    (event: KeyboardEvent) => {
      for (const shortcut of shortcuts) {
        const {
          key,
          ctrlKey = false,
          metaKey = false,
          shiftKey = false,
          altKey = false,
          action,
        } = shortcut

        // Check if the key combination matches
        if (
          event.key.toLowerCase() === key.toLowerCase() &&
          event.ctrlKey === ctrlKey &&
          event.metaKey === metaKey &&
          event.shiftKey === shiftKey &&
          event.altKey === altKey
        ) {
          event.preventDefault()
          action()
          break
        }
      }
    },
    [shortcuts]
  )

  useEffect(() => {
    document.addEventListener('keydown', handleKeyDown)
    return () => {
      document.removeEventListener('keydown', handleKeyDown)
    }
  }, [handleKeyDown])
}

// Predefined common keyboard shortcuts
export const KEYBOARD_SHORTCUTS = {
  COMMAND_PALETTE: { key: 'k', metaKey: true, ctrlKey: true },
  NEW_TASK: { key: 'n', metaKey: true, ctrlKey: true },
  SEARCH: { key: 'f', metaKey: true, ctrlKey: true },
  ESCAPE: { key: 'Escape' },
  SAVE: { key: 's', metaKey: true, ctrlKey: true },
  DELETE: { key: 'Delete' },
  REFRESH: { key: 'r', metaKey: true, ctrlKey: true },
  NEXT_ITEM: { key: 'j' },
  PREV_ITEM: { key: 'k' },
  SELECT_ITEM: { key: 'Enter' },
  CLOSE: { key: 'Escape' },
} as const

export function useGlobalKeyboardShortcuts() {
  useKeyboardShortcuts([
    {
      ...KEYBOARD_SHORTCUTS.COMMAND_PALETTE,
      action: () => {
        // Command palette is handled in CommandMenu component
        console.log('Command palette shortcut triggered')
      },
      description: 'Open command palette',
    },
  ])
}