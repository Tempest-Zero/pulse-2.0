"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Navigation } from "@/components/navigation"
import { Sparkles, Brain, Target, Zap, Shield, TrendingUp, Clock, Heart, Coffee } from "lucide-react"

export default function PulsePage() {
  const [isHovered, setIsHovered] = useState(false)

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      {/* Hero Section */}
      <header className="relative overflow-hidden">
        <div className="container mx-auto px-4 py-20 md:py-32">
          <div className="max-w-4xl mx-auto text-center">
            <div className="inline-flex items-center gap-2 bg-accent/20 text-accent-foreground px-4 py-2 rounded-full mb-8">
              <Sparkles className="w-4 h-4" />
              <span className="text-sm font-medium">Your AI productivity sidekick</span>
            </div>

            <h1 className="text-5xl md:text-7xl font-bold mb-6 text-balance leading-tight">
              Stop fighting your brain. <span className="text-accent">Start vibing</span> with it.
            </h1>

            <p className="text-xl md:text-2xl text-muted-foreground mb-10 text-pretty leading-relaxed max-w-2xl mx-auto">
              Pulse is your AI coach that actually gets you. No judgment, no boring timers—just real support when you
              need it most.
            </p>

            <div className="flex flex-col sm:flex-row items-center justify-center gap-4 mb-12">
              <Button
                size="lg"
                className="bg-accent text-accent-foreground hover:bg-accent/90 text-lg px-8 py-6 rounded-2xl"
                onMouseEnter={() => setIsHovered(true)}
                onMouseLeave={() => setIsHovered(false)}
              >
                <Zap className={`w-5 h-5 mr-2 ${isHovered ? "animate-pulse" : ""}`} />
                Start for Free
              </Button>
              <Button size="lg" variant="outline" className="text-lg px-8 py-6 rounded-2xl bg-transparent">
                Watch Demo
              </Button>
            </div>

            {/* Social Proof */}
            <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
              <div className="flex items-center gap-2">
                <div className="flex -space-x-2">
                  {[1, 2, 3, 4].map((i) => (
                    <div key={i} className="w-8 h-8 rounded-full bg-accent border-2 border-background" />
                  ))}
                </div>
                <span>10k+ users staying focused</span>
              </div>
              <div className="flex items-center gap-2">
                <span className="text-accent">★★★★★</span>
                <span>4.9/5 on Product Hunt</span>
              </div>
            </div>
          </div>
        </div>

        {/* Decorative Background Elements */}
        <div className="absolute top-0 right-0 w-96 h-96 bg-accent/10 rounded-full blur-3xl -z-10" />
        <div className="absolute bottom-0 left-0 w-96 h-96 bg-primary/10 rounded-full blur-3xl -z-10" />
      </header>

      {/* Features Grid */}
      <section id="features" className="py-20 md:py-32 bg-muted/30">
        <div className="container mx-auto px-4">
          <div className="text-center mb-16">
            <h2 className="text-4xl md:text-5xl font-bold mb-4">Built different, for real</h2>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Not another productivity app that collects dust. This one actually works with how your brain operates.
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6 max-w-6xl mx-auto">
            {[
              {
                icon: Brain,
                title: "AI That Gets You",
                description:
                  "Your coach learns your patterns, mood, and energy levels. No two days are the same, and neither is your schedule.",
                color: "text-accent",
              },
              {
                icon: Shield,
                title: "Distraction Shield",
                description:
                  "Auto-blocks social media when you need to lock in. Your phone becomes a tool, not a trap.",
                color: "text-chart-2",
              },
              {
                icon: Target,
                title: "Smart Focus Sessions",
                description:
                  "Adapts to your energy. Feeling it? Longer sessions. Burnt out? Shorter sprints. It just knows.",
                color: "text-chart-3",
              },
              {
                icon: Heart,
                title: "Mood-First Planning",
                description:
                  "Daily check-ins that actually matter. Tell Pulse how you're feeling and watch your day adjust.",
                color: "text-chart-4",
              },
              {
                icon: TrendingUp,
                title: "Real Progress Tracking",
                description:
                  "See your streaks, patterns, and wins. Celebrate the small stuff that leads to big changes.",
                color: "text-chart-1",
              },
              {
                icon: Coffee,
                title: "Break Reminders",
                description: "Hustle culture is toxic. Pulse reminds you to actually rest, hydrate, and touch grass.",
                color: "text-chart-5",
              },
            ].map((feature, i) => (
              <Card key={i} className="p-6 hover:shadow-lg transition-shadow group cursor-pointer border-border/50">
                <feature.icon
                  className={`w-12 h-12 mb-4 ${feature.color} group-hover:scale-110 transition-transform`}
                />
                <h3 className="text-xl font-bold mb-2">{feature.title}</h3>
                <p className="text-muted-foreground leading-relaxed">{feature.description}</p>
              </Card>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20 md:py-32">
        <div className="container mx-auto px-4">
          <div className="max-w-5xl mx-auto">
            <div className="text-center mb-16">
              <h2 className="text-4xl md:text-5xl font-bold mb-4">How it works (it\'s actually simple)</h2>
              <p className="text-xl text-muted-foreground">Four steps to unlock your most productive self</p>
            </div>

            <div className="grid md:grid-cols-2 gap-8">
              {[
                {
                  step: "01",
                  title: "Download & Connect",
                  description:
                    "Install Pulse on your phone and desktop. Give it permission to understand your app usage (we keep everything private, promise).",
                  icon: Sparkles,
                },
                {
                  step: "02",
                  title: "Daily Check-Ins",
                  description:
                    "Every evening, write how you felt today. Good vibes? Struggling? Your AI coach reads it and adjusts tomorrow's plan.",
                  icon: Heart,
                },
                {
                  step: "03",
                  title: "Smart Blocking",
                  description:
                    "During focus time, distracting apps get blocked automatically. No willpower needed—Pulse has your back.",
                  icon: Shield,
                },
                {
                  step: "04",
                  title: "Watch It Adapt",
                  description:
                    "The more you use it, the smarter it gets. Your schedule evolves with you, not against you.",
                  icon: Brain,
                },
              ].map((item, i) => (
                <div key={i} className="relative">
                  <Card className="p-8 h-full border-border/50 hover:border-accent/50 transition-colors">
                    <div className="flex items-start gap-4">
                      <div className="text-6xl font-bold text-accent/20">{item.step}</div>
                      <div className="flex-1">
                        <div className="flex items-center gap-3 mb-3">
                          <item.icon className="w-6 h-6 text-accent" />
                          <h3 className="text-2xl font-bold">{item.title}</h3>
                        </div>
                        <p className="text-muted-foreground leading-relaxed">{item.description}</p>
                      </div>
                    </div>
                  </Card>
                </div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-20 bg-primary text-primary-foreground">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-3 gap-12 max-w-4xl mx-auto text-center">
            <div>
              <div className="text-5xl md:text-6xl font-bold mb-2">2.5x</div>
              <div className="text-lg opacity-90">More productive days per week</div>
            </div>
            <div>
              <div className="text-5xl md:text-6xl font-bold mb-2">78%</div>
              <div className="text-lg opacity-90">Less time wasted on social media</div>
            </div>
            <div>
              <div className="text-5xl md:text-6xl font-bold mb-2">10k+</div>
              <div className="text-lg opacity-90">People finally getting stuff done</div>
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-20 md:py-32">
        <div className="container mx-auto px-4">
          <Card className="max-w-4xl mx-auto p-12 text-center bg-accent/5 border-accent/20">
            <Clock className="w-16 h-16 mx-auto mb-6 text-accent" />
            <h2 className="text-4xl md:text-5xl font-bold mb-6 text-balance">Ready to stop procrastinating?</h2>
            <p className="text-xl text-muted-foreground mb-8 max-w-2xl mx-auto">
              Join thousands of people who are finally getting their lives together (no judgment, we\'ve all been
              there).
            </p>
            <div className="flex flex-col sm:flex-row items-center justify-center gap-4">
              <Button
                size="lg"
                className="bg-accent text-accent-foreground hover:bg-accent/90 text-lg px-8 py-6 rounded-2xl"
              >
                <Zap className="w-5 h-5 mr-2" />
                Start Free Trial
              </Button>
              <p className="text-sm text-muted-foreground">No credit card required • 14-day free trial</p>
            </div>
          </Card>
        </div>
      </section>

      {/* Footer */}
      <footer className="py-12 border-t border-border/50">
        <div className="container mx-auto px-4">
          <div className="flex flex-col md:flex-row items-center justify-between gap-6">
            <div className="flex items-center gap-2">
              <div className="w-8 h-8 rounded-lg bg-primary flex items-center justify-center">
                <Sparkles className="w-5 h-5 text-primary-foreground" />
              </div>
              <span className="text-lg font-bold">Pulse</span>
            </div>
            <div className="flex flex-wrap items-center justify-center gap-6 text-sm text-muted-foreground">
              <a href="#" className="hover:text-foreground transition-colors">
                Privacy
              </a>
              <a href="#" className="hover:text-foreground transition-colors">
                Terms
              </a>
              <a href="#" className="hover:text-foreground transition-colors">
                Support
              </a>
              <a href="#" className="hover:text-foreground transition-colors">
                Blog
              </a>
            </div>
            <div className="text-sm text-muted-foreground">© 2025 Pulse. Made with ❤️ for productivity nerds.</div>
          </div>
        </div>
      </footer>
    </div>
  )
}
