/**
 * Settings Page - User Preferences & Configuration
 * 
 * Features:
 * 1. Theme settings
 * 2. Notification preferences
 * 3. Keyboard shortcut customization
 * 4. Account settings
 */

'use client'

import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card'
import { Label } from '@/components/ui/label'
import { Button } from '@/components/ui/button'
import { Switch } from '@/components/ui/switch'
import { Bell, Keyboard, Palette, User } from 'lucide-react'
import { Separator } from '@/components/ui/separator'

export default function SettingsPage() {
  return (
    <div className="flex-1 space-y-4 p-4 md:p-8 pt-6">
      <div className="space-y-2">
        <h2 className="text-3xl font-bold tracking-tight">Settings</h2>
        <p className="text-muted-foreground">
          Manage your preferences and account settings
        </p>
      </div>

      <Separator />

      <div className="grid gap-6">
        {/* Appearance Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Palette className="h-5 w-5" />
              <CardTitle>Appearance</CardTitle>
            </div>
            <CardDescription>
              Customize the look and feel of the application
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Dark Mode</Label>
                <div className="text-sm text-muted-foreground">
                  Toggle dark mode on or off
                </div>
              </div>
              <Switch />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Compact View</Label>
                <div className="text-sm text-muted-foreground">
                  Use a more compact layout for tables
                </div>
              </div>
              <Switch />
            </div>
          </CardContent>
        </Card>

        {/* Notification Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Bell className="h-5 w-5" />
              <CardTitle>Notifications</CardTitle>
            </div>
            <CardDescription>
              Configure when and how you receive notifications
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Task Updates</Label>
                <div className="text-sm text-muted-foreground">
                  Get notified when tasks are updated
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Priority Changes</Label>
                <div className="text-sm text-muted-foreground">
                  Get notified when AI changes task priorities
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Email Notifications</Label>
                <div className="text-sm text-muted-foreground">
                  Receive notifications via email
                </div>
              </div>
              <Switch />
            </div>
          </CardContent>
        </Card>

        {/* Keyboard Shortcuts */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <Keyboard className="h-5 w-5" />
              <CardTitle>Keyboard Shortcuts</CardTitle>
            </div>
            <CardDescription>
              View and customize keyboard shortcuts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="space-y-2">
              <div className="flex items-center justify-between py-2">
                <span className="text-sm">Open Command Palette</span>
                <kbd className="px-2 py-1 bg-muted rounded border text-sm">⌘K</kbd>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm">Navigate Up</span>
                <kbd className="px-2 py-1 bg-muted rounded border text-sm">K</kbd>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm">Navigate Down</span>
                <kbd className="px-2 py-1 bg-muted rounded border text-sm">J</kbd>
              </div>
              <div className="flex items-center justify-between py-2">
                <span className="text-sm">Select Item</span>
                <kbd className="px-2 py-1 bg-muted rounded border text-sm">Enter</kbd>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Account Settings */}
        <Card>
          <CardHeader>
            <div className="flex items-center gap-2">
              <User className="h-5 w-5" />
              <CardTitle>Account</CardTitle>
            </div>
            <CardDescription>
              Manage your account settings and preferences
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="space-y-0.5">
                <Label>Session Timeout</Label>
                <div className="text-sm text-muted-foreground">
                  Automatically log out after 30 minutes of inactivity
                </div>
              </div>
              <Switch defaultChecked />
            </div>
            <div className="pt-4">
              <Button variant="destructive">
                Delete Account
              </Button>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  )
}
