"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Navigation } from "@/components/navigation"
import { Shield, Bell, Clock, Smartphone, Monitor, Moon, Sun } from "lucide-react"
import { useAuth } from "@/lib/auth-context"

export default function SettingsPage() {
  const { user } = useAuth()
  const [darkMode, setDarkMode] = useState(true)
  const [notifications, setNotifications] = useState(true)
  const [smartBlocking, setSmartBlocking] = useState(true)
  const [profileName, setProfileName] = useState("")
  const [profileEmail, setProfileEmail] = useState("")

  // Load user data from auth context
  useEffect(() => {
    if (user) {
      setProfileName(user.username || user.name || "")
      setProfileEmail(user.email || "")
    }
  }, [user])

  // Load blocked apps from localStorage or use defaults
  const loadBlockedApps = () => {
    try {
      const saved = localStorage.getItem('blockedApps')
      if (saved) {
        return JSON.parse(saved)
      }
    } catch (error) {
      console.log('Error loading blocked apps')
    }
    // Default apps
    return [
      { name: "Instagram", icon: "📷", blocked: true },
      { name: "TikTok", icon: "🎵", blocked: true },
      { name: "Twitter", icon: "🐦", blocked: true },
      { name: "YouTube", icon: "▶️", blocked: false },
      { name: "Reddit", icon: "🤖", blocked: true },
      { name: "Discord", icon: "💬", blocked: false },
    ]
  }

  const [blockedApps, setBlockedApps] = useState([])

  // Load blocked apps on mount
  useEffect(() => {
    setBlockedApps(loadBlockedApps())
  }, [])

  // Save blocked apps to localStorage whenever they change
  const updateBlockedApp = (index, blocked) => {
    const updated = [...blockedApps]
    updated[index] = { ...updated[index], blocked }
    setBlockedApps(updated)
    localStorage.setItem('blockedApps', JSON.stringify(updated))
    // Dispatch custom event for same-window updates
    window.dispatchEvent(new Event('blockedAppsUpdated'))
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Component */}
      <Navigation />

      <div className="container mx-auto px-4 py-8 max-w-4xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Settings</h1>
          <p className="text-muted-foreground text-lg">Make Pulse work exactly how you want it</p>
        </div>

        {/* Profile Section */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Profile</h2>
          <div className="flex items-center gap-6">
            <div className="w-20 h-20 rounded-full bg-accent flex items-center justify-center text-3xl">👤</div>
            <div className="flex-1">
              <input
                type="text"
                placeholder="Your name"
                className="w-full bg-muted px-4 py-3 rounded-lg mb-3 font-medium"
                value={profileName}
                onChange={(e) => setProfileName(e.target.value)}
              />
              <input
                type="email"
                placeholder="Email"
                className="w-full bg-muted px-4 py-3 rounded-lg font-medium"
                value={profileEmail}
                onChange={(e) => setProfileEmail(e.target.value)}
              />
            </div>
          </div>
          <Button className="mt-4">Save changes</Button>
        </Card>

        {/* App Blocking */}
        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Shield className="w-5 h-5 text-accent" />
                App blocking
              </h2>
              <p className="text-sm text-muted-foreground mt-1">Choose which apps to block during focus time</p>
            </div>
            <button
              onClick={() => setSmartBlocking(!smartBlocking)}
              className={`w-14 h-8 rounded-full transition-colors ${smartBlocking ? "bg-accent" : "bg-muted"} relative`}
            >
              <div
                className={`w-6 h-6 rounded-full bg-white absolute top-1 transition-transform ${smartBlocking ? "translate-x-7" : "translate-x-1"
                  }`}
              />
            </button>
          </div>
          <div className="grid md:grid-cols-2 gap-3">
            {blockedApps.map((app, i) => (
              <div key={i} className="flex items-center justify-between p-4 bg-muted rounded-lg">
                <div className="flex items-center gap-3">
                  <span className="text-2xl">{app.icon}</span>
                  <span className="font-medium">{app.name}</span>
                </div>
                <button
                  onClick={() => updateBlockedApp(i, !app.blocked)}
                  className={`w-12 h-7 rounded-full transition-colors ${app.blocked ? "bg-accent" : "bg-border"
                    } relative`}
                >
                  <div
                    className={`w-5 h-5 rounded-full bg-white absolute top-1 transition-transform ${app.blocked ? "translate-x-6" : "translate-x-1"
                      }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </Card>

        {/* Focus Settings */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Clock className="w-5 h-5 text-accent" />
            Focus sessions
          </h2>
          <div className="space-y-4">
            <div>
              <label className="text-sm font-medium mb-2 block">Default session length</label>
              <select className="w-full bg-muted px-4 py-3 rounded-lg font-medium">
                <option>25 minutes (Pomodoro)</option>
                <option>45 minutes</option>
                <option>60 minutes</option>
                <option>90 minutes (Deep work)</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Break duration</label>
              <select className="w-full bg-muted px-4 py-3 rounded-lg font-medium">
                <option>5 minutes</option>
                <option>10 minutes</option>
                <option>15 minutes</option>
              </select>
            </div>
            <div>
              <label className="text-sm font-medium mb-2 block">Daily focus goal</label>
              <input
                type="number"
                className="w-full bg-muted px-4 py-3 rounded-lg font-medium"
                defaultValue="4"
                placeholder="Hours"
              />
            </div>
          </div>
        </Card>

        {/* Notifications */}
        <Card className="p-6 mb-6">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h2 className="text-xl font-bold flex items-center gap-2">
                <Bell className="w-5 h-5 text-accent" />
                Notifications
              </h2>
              <p className="text-sm text-muted-foreground mt-1">Stay updated without being annoying</p>
            </div>
            <button
              onClick={() => setNotifications(!notifications)}
              className={`w-14 h-8 rounded-full transition-colors ${notifications ? "bg-accent" : "bg-muted"} relative`}
            >
              <div
                className={`w-6 h-6 rounded-full bg-white absolute top-1 transition-transform ${notifications ? "translate-x-7" : "translate-x-1"
                  }`}
              />
            </button>
          </div>
          <div className="space-y-3">
            {[
              { label: "Break reminders", enabled: true },
              { label: "Task completion celebrations", enabled: true },
              { label: "Daily check-in prompts", enabled: true },
              { label: "Weekly insights", enabled: false },
            ].map((item, i) => (
              <div key={i} className="flex items-center justify-between p-3 bg-muted rounded-lg">
                <span className="font-medium">{item.label}</span>
                <button
                  className={`w-12 h-7 rounded-full transition-colors ${item.enabled ? "bg-accent" : "bg-border"
                    } relative`}
                >
                  <div
                    className={`w-5 h-5 rounded-full bg-white absolute top-1 transition-transform ${item.enabled ? "translate-x-6" : "translate-x-1"
                      }`}
                  />
                </button>
              </div>
            ))}
          </div>
        </Card>

        {/* Connected Devices */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Connected devices</h2>
          <div className="space-y-3">
            <div className="flex items-center justify-between p-4 bg-accent/10 border border-accent/30 rounded-lg">
              <div className="flex items-center gap-3">
                <Smartphone className="w-5 h-5 text-accent" />
                <div>
                  <div className="font-medium">iPhone 14 Pro</div>
                  <div className="text-sm text-muted-foreground">Connected • Last sync 2 min ago</div>
                </div>
              </div>
              <Button variant="outline" size="sm">
                Disconnect
              </Button>
            </div>
            <div className="flex items-center justify-between p-4 bg-accent/10 border border-accent/30 rounded-lg">
              <div className="flex items-center gap-3">
                <Monitor className="w-5 h-5 text-accent" />
                <div>
                  <div className="font-medium">MacBook Pro</div>
                  <div className="text-sm text-muted-foreground">Connected • Last sync 5 min ago</div>
                </div>
              </div>
              <Button variant="outline" size="sm">
                Disconnect
              </Button>
            </div>
          </div>
          <Button variant="outline" className="w-full mt-4 bg-transparent">
            + Add new device
          </Button>
        </Card>

        {/* Appearance */}
        <Card className="p-6 mb-6">
          <h2 className="text-xl font-bold mb-4">Appearance</h2>
          <div className="flex items-center justify-between p-4 bg-muted rounded-lg">
            <div className="flex items-center gap-3">
              {darkMode ? <Moon className="w-5 h-5" /> : <Sun className="w-5 h-5" />}
              <span className="font-medium">Dark mode</span>
            </div>
            <button
              onClick={() => setDarkMode(!darkMode)}
              className={`w-14 h-8 rounded-full transition-colors ${darkMode ? "bg-accent" : "bg-border"} relative`}
            >
              <div
                className={`w-6 h-6 rounded-full bg-white absolute top-1 transition-transform ${darkMode ? "translate-x-7" : "translate-x-1"
                  }`}
              />
            </button>
          </div>
        </Card>

        {/* Danger Zone */}
        <Card className="p-6 border-destructive/50">
          <h2 className="text-xl font-bold mb-4 text-destructive">Danger zone</h2>
          <div className="space-y-3">
            <Button variant="outline" className="w-full text-destructive border-destructive/50 bg-transparent">
              Reset all data
            </Button>
            <Button variant="outline" className="w-full text-destructive border-destructive/50 bg-transparent">
              Delete account
            </Button>
          </div>
        </Card>
      </div>
    </div>
  )
}
