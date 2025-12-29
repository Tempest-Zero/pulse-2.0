"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Navigation } from "@/components/navigation"
import { TrendingUp, TrendingDown, Clock, Target, Brain, Zap, Shield, Heart, Coffee } from "lucide-react"
import { getReflections, getMoodAverage, getCommonDistractions } from "@/lib/api/reflections"
import { getMoodCounts, getMostCommonMood } from "@/lib/api/mood"
import { getTasks } from "@/lib/api/tasks"
import { useToast } from "@/hooks/use-toast"

export default function InsightsPage() {
  const { toast } = useToast()
  const [weekData, setWeekData] = useState([
    { day: "Mon", focus: 0, mood: 0 },
    { day: "Tue", focus: 0, mood: 0 },
    { day: "Wed", focus: 0, mood: 0 },
    { day: "Thu", focus: 0, mood: 0 },
    { day: "Fri", focus: 0, mood: 0 },
    { day: "Sat", focus: 0, mood: 0 },
    { day: "Sun", focus: 0, mood: 0 },
  ])
  const [stats, setStats] = useState({
    totalFocusTime: 0,
    tasksCompleted: 0,
    totalTasks: 0,
    avgProductivity: 0,
    breaksTaken: 0,
  })
  const [loading, setLoading] = useState(true)
  const [moodAverage, setMoodAverage] = useState(null)
  const [commonDistractions, setCommonDistractions] = useState([])
  const [mostCommonMood, setMostCommonMood] = useState(null)

  useEffect(() => {
    loadInsights()
  }, [])

  const loadInsights = async () => {
    try {
      setLoading(true)
      
      // Load reflections for mood data
      const reflections = await getReflections(7)
      
      // Load mood analytics
      const moodAvg = await getMoodAverage(7)
      setMoodAverage(moodAvg)
      
      const mostCommon = await getMostCommonMood(100)
      setMostCommonMood(mostCommon)
      
      // Load distractions
      const distractions = await getCommonDistractions(30)
      setCommonDistractions(distractions.distractions || [])
      
      // Load tasks for completion stats
      const allTasks = await getTasks()
      const completedTasks = allTasks.filter(t => t.completed).length
      const totalTasks = allTasks.length
      
      // Calculate focus time (sum of completed task durations)
      const totalFocusTime = allTasks
        .filter(t => t.completed)
        .reduce((sum, t) => sum + (t.duration || 0), 0)
      
      setStats({
        totalFocusTime: Math.round(totalFocusTime * 10) / 10, // Round to 1 decimal
        tasksCompleted: completedTasks,
        totalTasks: totalTasks,
        avgProductivity: totalTasks > 0 ? Math.round((completedTasks / totalTasks) * 100) : 0,
        breaksTaken: Math.floor(totalFocusTime / 2), // Estimate breaks
      })
      
      // Map reflections to week data (simplified - using last 7 reflections)
      if (reflections.length > 0) {
        const mappedData = reflections.slice(0, 7).reverse().map((reflection, index) => {
          const days = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat']
          return {
            day: days[index] || days[reflections.length - index - 1],
            focus: Math.min(100, (reflection.completedTasks / Math.max(1, reflection.totalTasks)) * 100),
            mood: reflection.moodScore || 3,
          }
        })
        
        // Fill remaining days with zeros
        while (mappedData.length < 7) {
          const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']
          mappedData.push({ day: days[mappedData.length], focus: 0, mood: 0 })
        }
        
        setWeekData(mappedData.slice(0, 7))
      }
    } catch (error) {
      toast({
        title: "Error loading insights",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

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
                {loading ? (
                  "Loading your insights..."
                ) : moodAverage && moodAverage.average_mood ? (
                  `Your average mood this week was ${moodAverage.average_mood.toFixed(1)}/5. ${mostCommonMood && mostCommonMood.most_common ? `Your most common mood is ${mostCommonMood.most_common}.` : ''} ${commonDistractions.length > 0 ? `Top distraction: ${commonDistractions[0]?.tag || 'N/A'}.` : ''} Keep tracking to see more patterns! 🔥`
                ) : (
                  "Start tracking your mood and reflections to see personalized insights here!"
                )}
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
            <div className="text-3xl font-bold mb-1">{loading ? '...' : `${stats.totalFocusTime}h`}</div>
            <div className="text-sm text-muted-foreground">Total focus time</div>
          </Card>
          <Card className="p-6 text-center">
            <Target className="w-10 h-10 mx-auto mb-3 text-chart-2" />
            <div className="text-3xl font-bold mb-1">{loading ? '...' : `${stats.tasksCompleted}/${stats.totalTasks}`}</div>
            <div className="text-sm text-muted-foreground">Tasks completed</div>
          </Card>
          <Card className="p-6 text-center">
            <Zap className="w-10 h-10 mx-auto mb-3 text-chart-3" />
            <div className="text-3xl font-bold mb-1">{loading ? '...' : `${stats.avgProductivity}%`}</div>
            <div className="text-sm text-muted-foreground">Avg productivity</div>
          </Card>
          <Card className="p-6 text-center">
            <Coffee className="w-10 h-10 mx-auto mb-3 text-chart-5" />
            <div className="text-3xl font-bold mb-1">{loading ? '...' : stats.breaksTaken}</div>
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
              {loading ? (
                <div className="text-center py-4 text-muted-foreground">Loading insights...</div>
              ) : (
                [
                  moodAverage && moodAverage.average_mood > 3.5 ? "Your mood has been consistently positive this week" : null,
                  stats.avgProductivity > 70 ? "You're completing most of your tasks - great job!" : null,
                  mostCommonMood && mostCommonMood.most_common === 'energized' ? "You're feeling energized most of the time" : null,
                  commonDistractions.length > 0 ? `Your top distraction is ${commonDistractions[0]?.tag || 'N/A'}` : null,
                ].filter(Boolean).map((insight, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-chart-2/10">
                    <div className="w-5 h-5 rounded-full bg-chart-2 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-xs text-white">✓</span>
                    </div>
                    <p className="text-sm leading-relaxed">{insight}</p>
                  </div>
                ))
              )}
            </div>
          </Card>

          <Card className="p-6">
            <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
              <TrendingDown className="w-5 h-5 text-chart-5" />
              Room for improvement
            </h3>
            <div className="space-y-3">
              {loading ? (
                <div className="text-center py-4 text-muted-foreground">Loading insights...</div>
              ) : (
                [
                  stats.avgProductivity < 50 ? "Try to complete more tasks to improve your productivity" : null,
                  commonDistractions.length > 0 && commonDistractions[0]?.count > 5 ? `You mentioned "${commonDistractions[0]?.tag}" frequently - consider blocking it during focus time` : null,
                  moodAverage && moodAverage.average_mood < 3 ? "Your mood has been lower this week - take more breaks" : null,
                  stats.totalFocusTime < 2 ? "Try to increase your focus time to see better results" : null,
                ].filter(Boolean).map((insight, i) => (
                  <div key={i} className="flex items-start gap-3 p-3 rounded-lg bg-chart-5/10">
                    <div className="w-5 h-5 rounded-full bg-chart-5 flex items-center justify-center flex-shrink-0 mt-0.5">
                      <span className="text-xs text-white">!</span>
                    </div>
                    <p className="text-sm leading-relaxed">{insight}</p>
                  </div>
                ))
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  )
}
