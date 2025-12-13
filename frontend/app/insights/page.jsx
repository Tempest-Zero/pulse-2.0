"use client"

import { Card } from "@/components/ui/card"
import { Navigation } from "@/components/navigation"
import { TrendingUp, TrendingDown, Clock, Target, Brain, Zap, Shield, Heart, Coffee } from "lucide-react"
import { useTasks, useMoodHistory, useReflections } from "@/hooks"

export default function InsightsPage() {
  // Real data from API
  const { data: tasks = [] } = useTasks()
  const { data: moodHistory = [] } = useMoodHistory(7)
  const { data: reflections = [] } = useReflections(7)

  // Calculate real stats
  const completedTasks = tasks.filter(t => t.done).length
  const totalTasks = tasks.length
  const completionRate = totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0

  // Mock week data for now (would need date-based API for real data)
  const weekData = [
    { day: "Mon", focus: 85, mood: 4 },
    { day: "Tue", focus: 72, mood: 3 },
    { day: "Wed", focus: 90, mood: 5 },
    { day: "Thu", focus: 65, mood: 3 },
    { day: "Fri", focus: 88, mood: 4 },
    { day: "Sat", focus: 45, mood: 4 },
    { day: "Sun", focus: 30, mood: 5 },
  ]

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation */}
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Your productivity patterns</h1>
          <p className="text-muted-foreground text-lg">Here's what the data says about you</p>
        </div>

        {/* AI Summary */}
        <Card className="p-8 mb-8 bg-gradient-to-br from-primary/10 to-accent/10 border-primary/30">
          <div className="flex items-start gap-4">
            <div className="w-16 h-16 rounded-2xl bg-primary flex items-center justify-center flex-shrink-0">
              <Brain className="w-8 h-8 text-primary-foreground" />
            </div>
            <div className="flex-1">
              <h2 className="text-2xl font-bold mb-3">This week's AI analysis</h2>
              <p className="text-lg leading-relaxed mb-4">
                You had a strong week! Your focus peaked on Wednesday with 3 hours of deep work. I noticed you struggle
                a bit on Thursdays—probably the mid-week slump. Your energy is highest between 2-5pm, so I've been
                scheduling heavy tasks then. Keep crushing it! 🔥
              </p>
              <div className="flex flex-wrap gap-3">
                <div className="flex items-center gap-2 bg-chart-2/20 text-chart-2 px-3 py-2 rounded-full text-sm font-medium">
                  <TrendingUp className="w-4 h-4" />
                  Focus improved by 15%
                </div>
                <div className="flex items-center gap-2 bg-accent/20 text-accent px-3 py-2 rounded-full text-sm font-medium">
                  <Target className="w-4 h-4" />
                  12-day streak
                </div>
                <div className="flex items-center gap-2 bg-chart-4/20 text-chart-4 px-3 py-2 rounded-full text-sm font-medium">
                  <Shield className="w-4 h-4" />
                  267 distractions blocked
                </div>
              </div>
            </div>
          </div>
        </Card>

        <div className="grid lg:grid-cols-2 gap-6 mb-8">
          {/* Focus Time Chart */}
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Clock className="w-5 h-5 text-accent" />
              Weekly focus time
            </h3>
            <div className="flex items-end justify-between gap-3 h-64">
              {weekData.map((day, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-3">
                  <div className="w-full relative flex items-end justify-center" style={{ height: "200px" }}>
                    <div
                      className="w-full bg-gradient-to-t from-accent to-accent/50 rounded-t-lg transition-all hover:scale-105 cursor-pointer"
                      style={{ height: `${day.focus}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-muted-foreground">{day.day}</span>
                </div>
              ))}
            </div>
          </Card>

          {/* Mood Tracker */}
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
              <Heart className="w-5 h-5 text-chart-4" />
              Mood patterns
            </h3>
            <div className="flex items-end justify-between gap-3 h-64">
              {weekData.map((day, i) => (
                <div key={i} className="flex-1 flex flex-col items-center gap-3">
                  <div className="w-full relative flex items-end justify-center" style={{ height: "200px" }}>
                    <div
                      className="w-full bg-gradient-to-t from-chart-4 to-chart-4/50 rounded-t-lg transition-all hover:scale-105 cursor-pointer"
                      style={{ height: `${day.mood * 20}%` }}
                    />
                  </div>
                  <span className="text-sm font-medium text-muted-foreground">{day.day}</span>
                </div>
              ))}
            </div>
          </Card>
        </div>

        {/* Quick Stats Grid */}
        <div className="grid md:grid-cols-4 gap-6 mb-8">
          <Card className="p-6 text-center">
            <Clock className="w-10 h-10 mx-auto mb-3 text-accent" />
            <div className="text-3xl font-bold mb-1">18.5h</div>
            <div className="text-sm text-muted-foreground">Total focus time</div>
          </Card>
          <Card className="p-6 text-center">
            <Target className="w-10 h-10 mx-auto mb-3 text-chart-2" />
            <div className="text-3xl font-bold mb-1">{completedTasks}/{totalTasks}</div>
            <div className="text-sm text-muted-foreground">Tasks completed</div>
          </Card>
          <Card className="p-6 text-center">
            <Zap className="w-10 h-10 mx-auto mb-3 text-chart-3" />
            <div className="text-3xl font-bold mb-1">{completionRate}%</div>
            <div className="text-sm text-muted-foreground">Completion rate</div>
          </Card>
          <Card className="p-6 text-center">
            <Coffee className="w-10 h-10 mx-auto mb-3 text-chart-5" />
            <div className="text-3xl font-bold mb-1">23</div>
            <div className="text-sm text-muted-foreground">Breaks taken</div>
          </Card>
        </div>

        {/* Insights Cards */}
        <div className="grid md:grid-cols-2 gap-6">
          <Card className="p-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingUp className="w-5 h-5 text-chart-2" />
              What's working
            </h3>
            <div className="space-y-3">
              {[
                "You're most productive between 2-5pm",
                "Taking short breaks every 45 mins helps your focus",
                "Morning workouts boost your afternoon energy",
                "Blocking social media increases focus by 40%",
              ].map((insight, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-chart-2/10">
                  <div className="w-5 h-5 rounded-full bg-chart-2 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs text-white">✓</span>
                  </div>
                  <p className="text-sm leading-relaxed">{insight}</p>
                </div>
              ))}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingDown className="w-5 h-5 text-chart-5" />
              Room for improvement
            </h3>
            <div className="space-y-3">
              {[
                "Thursday afternoons are your low-energy zone",
                "You check your phone 15x during focus sessions",
                "Late-night work sessions are 30% less productive",
                "Skipping breaks leads to burnout by 4pm",
              ].map((insight, i) => (
                <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-chart-5/10">
                  <div className="w-5 h-5 rounded-full bg-chart-5 flex items-center justify-center flex-shrink-0 mt-0.5">
                    <span className="text-xs text-white">!</span>
                  </div>
                  <p className="text-sm leading-relaxed">{insight}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
