"use client"

import Link from "next/link"
import { usePathname } from "next/navigation"
import { Button } from "@/components/ui/button"
import { Sparkles, LayoutDashboard, TrendingUp, Settings, Menu, X, CalendarDays } from "lucide-react"
import { useState, useEffect } from "react"

export function Navigation() {
  const pathname = usePathname()
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false)
  const isLanding = pathname === "/"

  // Close mobile menu on route change
  useEffect(() => {
    setMobileMenuOpen(false)
  }, [pathname])

  // Close mobile menu on escape key
  useEffect(() => {
    const handleEscape = (e) => {
      if (e.key === "Escape") setMobileMenuOpen(false)
    }
    document.addEventListener("keydown", handleEscape)
    return () => document.removeEventListener("keydown", handleEscape)
  }, [])

  const navLinks = isLanding
    ? [
      { href: "#features", label: "Features" },
      { href: "#how-it-works", label: "How it Works" },
      { href: "#pricing", label: "Pricing" },
    ]
    : [
      { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
      { href: "/schedule", label: "Schedule", icon: CalendarDays },
      { href: "/insights", label: "Insights", icon: TrendingUp },
      { href: "/settings", label: "Settings", icon: Settings },
    ]

  const isActive = (href) => {
    if (href.startsWith("#")) return false
    return pathname === href
  }

  return (
    <nav
      className="sticky top-0 z-50 bg-background/95 backdrop-blur-md border-b border-border/50 supports-[backdrop-filter]:bg-background/80"
      role="navigation"
      aria-label="Main navigation"
    >
      <div className="container mx-auto px-4 py-3 md:py-4 flex items-center justify-between">
        {/* Logo */}
        <Link
          href="/"
          className="flex items-center gap-2 group transition-transform hover:scale-[1.02] focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2 rounded-lg"
          aria-label="Pulse - Home"
        >
          <div className="w-9 h-9 md:w-10 md:h-10 rounded-xl bg-gradient-to-br from-accent to-accent/80 flex items-center justify-center shadow-lg shadow-accent/20 group-hover:shadow-accent/30 transition-shadow">
            <Sparkles className="w-5 h-5 md:w-6 md:h-6 text-accent-foreground" />
          </div>
          <span className="text-xl md:text-2xl font-bold bg-gradient-to-r from-foreground to-foreground/80 bg-clip-text">
            Pulse
          </span>
        </Link>

        {/* Desktop Navigation */}
        <div className="hidden md:flex items-center gap-1" role="menubar">
          {navLinks.map((link) => {
            const active = isActive(link.href)
            return (
              <Link
                key={link.href}
                href={link.href}
                role="menuitem"
                aria-current={active ? "page" : undefined}
                className={`
                  relative flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-all duration-200
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring focus-visible:ring-offset-2
                  ${active
                    ? "text-accent bg-accent/10"
                    : "text-muted-foreground hover:text-foreground hover:bg-muted/50"
                  }
                `}
              >
                {link.icon && <link.icon className={`w-4 h-4 ${active ? "text-accent" : ""}`} />}
                {link.label}
                {active && (
                  <span
                    className="absolute bottom-0 left-1/2 -translate-x-1/2 w-1/2 h-0.5 bg-accent rounded-full"
                    aria-hidden="true"
                  />
                )}
              </Link>
            )
          })}
        </div>

        {/* Desktop Actions */}
        <div className="hidden md:flex items-center gap-3">
          {isLanding ? (
            <>
              <Button
                variant="ghost"
                asChild
                className="text-muted-foreground hover:text-foreground"
              >
                <Link href="/auth">Sign In</Link>
              </Button>
              <Button
                asChild
                className="bg-accent text-accent-foreground hover:bg-accent/90 shadow-lg shadow-accent/20 hover:shadow-accent/30 transition-all"
              >
                <Link href="/auth">Get Started</Link>
              </Button>
            </>
          ) : (
            <Button
              variant="ghost"
              size="icon"
              asChild
              className="hover:bg-muted/50"
              aria-label="Settings"
            >
              <Link href="/settings">
                <Settings className="w-5 h-5" />
              </Link>
            </Button>
          )}
        </div>

        {/* Mobile Menu Button */}
        <Button
          variant="ghost"
          size="icon"
          className="md:hidden hover:bg-muted/50"
          onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
          aria-expanded={mobileMenuOpen}
          aria-controls="mobile-menu"
          aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
        >
          {mobileMenuOpen ? (
            <X className="w-6 h-6" aria-hidden="true" />
          ) : (
            <Menu className="w-6 h-6" aria-hidden="true" />
          )}
        </Button>
      </div>

      {/* Mobile Navigation */}
      <div
        id="mobile-menu"
        className={`
          md:hidden overflow-hidden transition-all duration-300 ease-in-out
          ${mobileMenuOpen ? "max-h-[400px] opacity-100" : "max-h-0 opacity-0"}
        `}
        aria-hidden={!mobileMenuOpen}
      >
        <div className="container mx-auto px-4 py-4 flex flex-col gap-2 border-t border-border/50 bg-background">
          {navLinks.map((link) => {
            const active = isActive(link.href)
            return (
              <Link
                key={link.href}
                href={link.href}
                onClick={() => setMobileMenuOpen(false)}
                tabIndex={mobileMenuOpen ? 0 : -1}
                aria-current={active ? "page" : undefined}
                className={`
                  flex items-center gap-3 px-4 py-3 rounded-xl text-base font-medium transition-all duration-200
                  focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-ring
                  ${active
                    ? "bg-accent/15 text-accent border border-accent/30"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground"
                  }
                `}
              >
                {link.icon && (
                  <link.icon className={`w-5 h-5 ${active ? "text-accent" : ""}`} aria-hidden="true" />
                )}
                {link.label}
              </Link>
            )
          })}
          {isLanding && (
            <div className="flex flex-col gap-2 pt-4 mt-2 border-t border-border/50">
              <Button
                variant="outline"
                asChild
                className="w-full justify-center"
              >
                <Link href="/auth" onClick={() => setMobileMenuOpen(false)} tabIndex={mobileMenuOpen ? 0 : -1}>
                  Sign In
                </Link>
              </Button>
              <Button
                asChild
                className="w-full justify-center bg-accent text-accent-foreground hover:bg-accent/90"
              >
                <Link href="/auth" onClick={() => setMobileMenuOpen(false)} tabIndex={mobileMenuOpen ? 0 : -1}>
                  Get Started
                </Link>
              </Button>
            </div>
          )}
        </div>
      </div>
    </nav>
  )
}
