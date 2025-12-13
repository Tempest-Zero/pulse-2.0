"use client"

import { useState } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Navigation } from "@/components/navigation"
import { Sparkles, Heart, Send, TrendingUp, Coffee, Zap } from "lucide-react"

export default function CheckinPage() {
  const [reflection, setReflection] = useState("")
  const [mood, setMood] = useState(null)
  const [energy, setEnergy] = useState(3)
  const [submitted, setSubmitted] = useState(false)

  const moods = [
    { emoji: "🔥", label: "On fire", value: 5 },
    { emoji: "😊", label: "Good", value: 4 },
    { emoji: "😐", label: "Meh", value: 3 },
    { emoji: "😓", label: "Struggling", value: 2 },
    { emoji: "💀", label: "Dead", value: 1 },
  ]

  const handleSubmit = () => {
    setSubmitted(true)
  }

  if (submitted) {
    return (
      <div className="min-h-screen bg-background flex items-center justify-center p-4">
        <Card className="max-w-2xl w-full p-12 text-center bg-gradient-to-br from-accent/10 to-primary/10 border-accent/30">
          <div className="w-20 h-20 rounded-full bg-accent mx-auto mb-6 flex items-center justify-center">
            <Sparkles className="w-10 h-10 text-accent-foreground" />
          </div>
          <h1 className="text-4xl font-bold mb-4">Thanks for sharing, bestie!</h1>
          <p className="text-xl text-muted-foreground mb-8">
            I've analyzed your reflection and I'm already working on tomorrow's schedule. Here's what I noticed:
          </p>
          <div className="space-y-4 text-left mb-8">
            <div className="p-4 bg-chart-2/10 rounded-lg border border-chart-2/30">
              <div className="flex items-center gap-2 mb-2">
                <TrendingUp className="w-5 h-5 text-chart-2" />
                <span className="font-bold">Energy pattern detected</span>
              </div>
              <p className="text-sm text-muted-foreground">
                You mentioned feeling tired by 4pm. I'll schedule lighter tasks for late afternoon tomorrow.
              </p>
            </div>
            <div className="p-4 bg-accent/10 rounded-lg border border-accent/30">
              <div className="flex items-center gap-2 mb-2">
                <Zap className="w-5 h-5 text-accent" />
                <span className="font-bold">Focus improvement</span>
              </div>
              <p className="text-sm text-muted-foreground">
                Your focus was strong today! I'll keep the same blocking patterns for tomorrow.
              </p>
            </div>
            <div className="p-4 bg-chart-4/10 rounded-lg border border-chart-4/30">
              <div className="flex items-center gap-2 mb-2">
                <Coffee className="w-5 h-5 text-chart-4" />
                <span className="font-bold">Break reminder</span>
              </div>
              <p className="text-sm text-muted-foreground">
                You skipped breaks today. Tomorrow I'll be more persistent about rest time.
              </p>
            </div>
          </div>
          <Button size="lg" className="bg-accent text-accent-foreground hover:bg-accent/90" asChild>
            <a href="/dashboard">Back to Dashboard</a>
          </Button>
        </Card>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Component */}
      <Navigation />

      <div className="container mx-auto px-4 py-12 max-w-3xl">
        <div className="text-center mb-12">
          <div className="w-16 h-16 rounded-full bg-accent/20 mx-auto mb-6 flex items-center justify-center">
            <Heart className="w-8 h-8 text-accent" />
          </div>
          <h1 className="text-5xl font-bold mb-4">How was your day?</h1>
          <p className="text-xl text-muted-foreground">
            Be honest—I'm here to help, not judge. The more you share, the better I can support you tomorrow.
          </p>
        </div>

        {/* Mood Selection */}
        <Card className="p-8 mb-6">
          <h2 className="text-2xl font-bold mb-6">How are you feeling?</h2>
          <div className="flex flex-wrap gap-4 justify-center">
            {moods.map((m) => (
              <button
                key={m.value}
                onClick={() => setMood(m.value)}
                className={`flex flex-col items-center gap-3 p-6 rounded-2xl border-2 transition-all ${
                  mood === m.value
                    ? "border-accent bg-accent/10 scale-110"
                    : "border-border/50 hover:border-accent/50 hover:scale-105"
                }`}
              >
                <span className="text-5xl">{m.emoji}</span>
                <span className="font-medium">{m.label}</span>
              </button>
            ))}
          </div>
        </Card>

        {/* Energy Level */}
        <Card className="p-8 mb-6">
          <h2 className="text-2xl font-bold mb-6">What's your energy level?</h2>
          <div className="flex items-center gap-4">
            <span className="text-sm font-medium text-muted-foreground">Dead</span>
            <input
              type="range"
              min="1"
              max="5"
              value={energy}
              onChange={(e) => setEnergy(Number.parseInt(e.target.value))}
              className="flex-1 h-3 rounded-lg appearance-none cursor-pointer accent-accent"
            />
            <span className="text-sm font-medium text-muted-foreground">Energized</span>
          </div>
          <div className="text-center mt-4">
            <span className="text-4xl">
              {energy === 1 && "💀"}
              {energy === 2 && "😴"}
              {energy === 3 && "😐"}
              {energy === 4 && "😊"}
              {energy === 5 && "⚡"}
            </span>
          </div>
        </Card>

        {/* Daily Reflection */}
        <Card className="p-8 mb-8">
          <h2 className="text-2xl font-bold mb-4">Tell me about your day</h2>
          <p className="text-muted-foreground mb-4">
            What went well? What was hard? Any patterns you noticed? Write whatever comes to mind—this is your space.
          </p>
          <textarea
            value={reflection}
            onChange={(e) => setReflection(e.target.value)}
            placeholder="Today was..."
            className="w-full bg-muted px-4 py-4 rounded-lg min-h-64 font-medium resize-none"
          />
          <div className="flex items-center justify-between mt-4 text-sm text-muted-foreground">
            <span>{reflection.length} characters</span>
            <span>💡 Tip: Be specific about what distracted you</span>
          </div>
        </Card>

        {/* Submit Button */}
        <Button
          size="lg"
          onClick={handleSubmit}
          disabled={!mood || !reflection}
          className="w-full bg-accent text-accent-foreground hover:bg-accent/90 text-lg py-6 rounded-2xl"
        >
          <Send className="w-5 h-5 mr-2" />
          Submit Check-in
        </Button>
      </div>
    </div>
  )
}
