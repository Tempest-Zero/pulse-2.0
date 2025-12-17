"use client"

import { useState, useEffect, useRef } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Navigation } from "@/components/navigation"
import { useAuth } from "@/lib/auth-context"
import { getTasks, createTask, updateTask, deleteTask, toggleTask, transformTask } from "@/lib/api/tasks"
import { setMood, getCurrentMood } from "@/lib/api/mood"
import { getScheduleBlocks, transformScheduleBlock } from "@/lib/api/schedule"
import { getReflections, getTodayReflection, createReflection } from "@/lib/api/reflections"
import { useToast } from "@/hooks/use-toast"
import { AIRecommendation } from "@/components/ai-recommendation"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
} from "@/components/ui/dialog"
import { Label } from "@/components/ui/label"
import { Textarea } from "@/components/ui/textarea"
import { Input } from "@/components/ui/input"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar } from "@/components/ui/calendar"
import { format } from "date-fns"
import {
  Sparkles,
  Play,
  Pause,
  SkipForward,
  TrendingUp,
  Clock,
  Zap,
  Coffee,
  Shield,
  Heart,
  CheckCircle2,
  CalendarIcon,
  Moon,
  Bell,
  Home,
  HelpCircle,
  Users,
  AlertCircle,
} from "lucide-react"

export default function DashboardPage() {
  const { toast } = useToast()
  const { isAuthenticated, loading: authLoading } = useAuth()
  const [isInSession, setIsInSession] = useState(false)
  const [sessionTime, setSessionTime] = useState(25 * 60)
  const [initialSessionTime] = useState(25 * 60) // Store initial time for reset
  const [mood, setMood] = useState(null)
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false)
  const [tasks, setTasks] = useState([])
  const [loading, setLoading] = useState(true)
  const [blockedAppsCount, setBlockedAppsCount] = useState(0)
  const [schedule, setSchedule] = useState([])
  const [stats, setStats] = useState({
    streak: 0,
    focusTime: 0,
    tasksCompleted: 0,
    totalTasks: 0,
    distractionsBlocked: 0,
    focusTimeGoal: 4 * 60, // 4 hours in minutes
  })
  const [todayReflection, setTodayReflection] = useState(null)
  const timerRef = useRef(null)
  const [taskForm, setTaskForm] = useState({
    name: "",
    priority: "",
    difficulty: "",
    estimatedTime: "",
    deadline: null,
  })
  const [isEndDayOpen, setIsEndDayOpen] = useState(false)
  const [endDayMood, setEndDayMood] = useState(3) // Default to middle (3)
  const [selectedDistractions, setSelectedDistractions] = useState([])
  const [endDayNote, setEndDayNote] = useState("")
  const [submittingEndDay, setSubmittingEndDay] = useState(false)

  // Fetch tasks, mood, schedule, and blocked apps count ONLY when authenticated
  // This fixes the race condition where API calls fire before token is ready
  useEffect(() => {
    // Wait for auth to finish loading and ensure we're authenticated
    if (authLoading || !isAuthenticated) {
      return
    }

    loadTasks()
    loadCurrentMood()
    loadSchedule()
    loadBlockedAppsCount()
    loadTodayReflection()
    calculateStats()

    // Listen for storage changes (when settings are updated in another tab/window)
    const handleStorageChange = (e) => {
      if (e.key === 'blockedApps') {
        loadBlockedAppsCount()
      }
    }
    window.addEventListener('storage', handleStorageChange)

    // Also listen for custom event (same window)
    const handleCustomStorageChange = () => {
      loadBlockedAppsCount()
    }
    window.addEventListener('blockedAppsUpdated', handleCustomStorageChange)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      window.removeEventListener('blockedAppsUpdated', handleCustomStorageChange)
    }
  }, [isAuthenticated, authLoading])

  // Recalculate stats when tasks or todayReflection change
  useEffect(() => {
    if (tasks.length >= 0) { // Only calculate if tasks have been loaded (even if empty)
      calculateStats()
    }
  }, [tasks, todayReflection, blockedAppsCount])

  // Refresh stats when page becomes visible or when reflection is submitted
  useEffect(() => {
    const handleVisibilityChange = () => {
      if (!document.hidden) {
        loadTodayReflection()
        calculateStats()
      }
    }

    const handleReflectionSubmitted = () => {
      loadTodayReflection()
      calculateStats()
    }

    document.addEventListener('visibilitychange', handleVisibilityChange)
    window.addEventListener('reflectionSubmitted', handleReflectionSubmitted)

    return () => {
      document.removeEventListener('visibilitychange', handleVisibilityChange)
      window.removeEventListener('reflectionSubmitted', handleReflectionSubmitted)
    }
  }, [])

  // Timer effect
  useEffect(() => {
    if (isInSession && sessionTime > 0) {
      timerRef.current = setInterval(() => {
        setSessionTime((prev) => {
          if (prev <= 1) {
            setIsInSession(false)
            toast({
              title: "Focus session complete!",
              description: "Great job! Time for a break 🎉",
            })
            return 0
          }
          return prev - 1
        })
      }, 1000)
    } else {
      if (timerRef.current) {
        clearInterval(timerRef.current)
        timerRef.current = null
      }
    }

    return () => {
      if (timerRef.current) {
        clearInterval(timerRef.current)
      }
    }
  }, [isInSession, sessionTime, toast])

  const loadTasks = async () => {
    try {
      setLoading(true)
      const data = await getTasks()
      setTasks(data.map(transformTask))
      // Stats will be recalculated by useEffect when tasks change
    } catch (error) {
      toast({
        title: "Error loading tasks",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const loadCurrentMood = async () => {
    try {
      const data = await getCurrentMood()
      if (data.mood) {
        // Map backend mood to frontend mood
        const moodMap = {
          'energized': 'energized',
          'calm': 'good',
          'focused': 'neutral',
          'tired': 'low',
        }
        setMood(moodMap[data.mood] || 'neutral')
      }
    } catch (error) {
      // Mood might not be set yet, that's okay - no need to log
    }
  }

  const loadSchedule = async () => {
    try {
      const data = await getScheduleBlocks()
      setSchedule(data.map(transformScheduleBlock))
    } catch (error) {
      // No schedule blocks yet - this is expected, not an error
    }
  }

  const loadBlockedAppsCount = () => {
    // Get blocked apps from localStorage (set by settings page)
    // Only access localStorage on client side
    if (typeof window === 'undefined') {
      setBlockedAppsCount(0)
      return
    }

    try {
      const savedBlockedApps = localStorage.getItem('blockedApps')
      if (savedBlockedApps) {
        const apps = JSON.parse(savedBlockedApps)
        const count = apps.filter(app => app.blocked === true).length
        setBlockedAppsCount(count)
      } else {
        // Default count from settings page structure
        setBlockedAppsCount(4) // Instagram, TikTok, Twitter, Reddit are blocked by default
      }
    } catch (error) {
      setBlockedAppsCount(0)
    }
  }

  const loadTodayReflection = async () => {
    try {
      const reflection = await getTodayReflection()
      setTodayReflection(reflection)
    } catch (error) {
      // No reflection for today yet - this is expected, not an error
      setTodayReflection(null)
    }
  }

  const calculateStreak = async () => {
    try {
      const reflections = await getReflections(100) // Get last 100 reflections
      if (reflections.length === 0) return 0

      // Sort by date descending (most recent first)
      reflections.sort((a, b) => new Date(b.date) - new Date(a.date))

      let streak = 0
      const today = new Date()
      today.setHours(0, 0, 0, 0)

      // Start checking from today
      let checkDate = new Date(today)

      // Count consecutive days with reflections, going backwards
      for (const reflection of reflections) {
        const reflectionDate = new Date(reflection.date)
        reflectionDate.setHours(0, 0, 0, 0)

        // If this reflection is for the date we're checking, increment streak and move to previous day
        if (reflectionDate.getTime() === checkDate.getTime()) {
          streak++
          checkDate.setDate(checkDate.getDate() - 1)
        } else if (reflectionDate.getTime() < checkDate.getTime()) {
          // We've passed the date we're looking for, gap found - break streak
          break
        }
        // If reflectionDate > checkDate, skip it (it's in the future or we haven't reached that date yet)
      }

      return streak
    } catch (error) {
      // Error calculating streak - return 0 silently
      return 0
    }
  }

  const calculateStats = async () => {
    try {
      // Calculate focus time from completed tasks (duration in minutes)
      const completedTasks = tasks.filter(t => t.completed)
      const focusTimeMinutes = completedTasks.reduce((sum, task) => {
        return sum + (task.duration || 0)
      }, 0)

      // Tasks stats
      const tasksCompleted = completedTasks.length
      const totalTasks = tasks.length

      // Distractions blocked - from today's reflection or use blocked apps count as estimate
      let distractionsBlocked = blockedAppsCount
      if (todayReflection && todayReflection.distractions) {
        distractionsBlocked = todayReflection.distractions.length || blockedAppsCount
      }

      // Calculate streak (only if we have reflections loaded)
      const streak = await calculateStreak()

      setStats(prevStats => ({
        ...prevStats,
        streak,
        focusTime: focusTimeMinutes,
        tasksCompleted,
        totalTasks,
        distractionsBlocked,
      }))
    } catch (error) {
      // Error calculating stats - silently fail
    }
  }

  const handleStartFocus = () => {
    if (sessionTime === 0) {
      setSessionTime(initialSessionTime)
    }
    setIsInSession(true)
  }

  const handlePauseFocus = () => {
    setIsInSession(false)
  }

  const handleMoodSelect = async (moodValue) => {
    try {
      await setMood(moodValue)
      setMood(moodValue)
      toast({
        title: "Mood saved",
        description: "Your mood has been saved successfully",
      })
    } catch (error) {
      toast({
        title: "Error saving mood",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const moods = [
    { emoji: "🔥", label: "On fire", value: "energized" },
    { emoji: "😊", label: "Vibing", value: "good" },
    { emoji: "😐", label: "Meh", value: "neutral" },
    { emoji: "😓", label: "Struggling", value: "low" },
    { emoji: "💀", label: "Dead", value: "exhausted" },
  ]

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, "0")}`
  }

  return (
    <div className="min-h-screen bg-background">
      {/* Navigation Component */}
      <Navigation />

      <div className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl font-bold mb-2">Welcome back, bestie</h1>
          <p className="text-muted-foreground text-lg">How are we feeling today?</p>
        </div>

        {/* Mood Check */}
        <Card className="p-6 mb-8 bg-accent/5 border-accent/20">
          <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
            <Heart className="w-5 h-5 text-accent" />
            Quick vibe check
          </h2>
          <div className="flex flex-wrap gap-3">
            {moods.map((m) => (
              <button
                key={m.value}
                onClick={() => handleMoodSelect(m.value)}
                className={`flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all ${mood === m.value
                  ? "border-accent bg-accent/10 scale-105"
                  : "border-border/50 hover:border-accent/50 hover:scale-105"
                  }`}
              >
                <span className="text-3xl">{m.emoji}</span>
                <span className="text-sm font-medium">{m.label}</span>
              </button>
            ))}
          </div>
          {mood && (
            <p className="mt-4 text-sm text-muted-foreground">
              Got it! I'll adjust your schedule to match your energy ✨
            </p>
          )}
        </Card>

        {/* AI Recommendation */}
        <AIRecommendation
          onStartFocus={(task) => {
            // Start focus session with recommended task
            setSessionTime(task.duration * 60)
            setIsInSession(true)
            toast({
              title: "Focus session started",
              description: `Starting focus on: ${task.title}`,
            })
          }}
        />

        <div className="grid lg:grid-cols-3 gap-6">
          {/* Focus Session - Main Column */}
          <div className="lg:col-span-2 space-y-6">
            {/* Active Session Card */}
            <Card className="p-8 bg-gradient-to-br from-primary/10 to-accent/10 border-accent/30">
              <div className="text-center">
                <div className="inline-flex items-center gap-2 bg-accent/20 text-accent-foreground px-3 py-1 rounded-full mb-6">
                  <Zap className="w-4 h-4" />
                  <span className="text-sm font-medium">Deep Work Mode</span>
                </div>

                <div className="text-8xl font-bold mb-6 font-mono">{formatTime(sessionTime)}</div>

                <div className="flex items-center justify-center gap-4 mb-6">
                  <Button
                    size="lg"
                    onClick={isInSession ? handlePauseFocus : handleStartFocus}
                    className="bg-accent text-accent-foreground hover:bg-accent/90 rounded-2xl"
                  >
                    {isInSession ? (
                      <>
                        <Pause className="w-5 h-5 mr-2" />
                        Pause
                      </>
                    ) : (
                      <>
                        <Play className="w-5 h-5 mr-2" />
                        Start Focus
                      </>
                    )}
                  </Button>
                  <Button
                    variant="outline"
                    size="lg"
                    className="rounded-2xl bg-transparent"
                    onClick={() => {
                      setIsInSession(false)
                      setSessionTime(initialSessionTime)
                    }}
                  >
                    <SkipForward className="w-5 h-5 mr-2" />
                    Reset
                  </Button>
                </div>

                <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                  <Shield className="w-4 h-4" />
                  <span>{blockedAppsCount} distracting {blockedAppsCount === 1 ? 'app' : 'apps'} blocked</span>
                </div>
              </div>
            </Card>

            {/* Schedule Breakdown */}
            {schedule.length > 0 && (
              <Card className="p-6">
                <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <CalendarIcon className="w-5 h-5 text-accent" />
                  Today's Schedule
                </h2>
                <div className="space-y-3">
                  {schedule.map((block, index) => (
                    <div
                      key={block.id || index}
                      className="flex items-center justify-between p-4 rounded-xl border bg-muted/30 border-border/50"
                    >
                      <div className="flex items-center gap-3 flex-1">
                        <div className="w-2 h-2 rounded-full bg-accent" />
                        <div>
                          <p className="font-medium">{block.name || block.title}</p>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {block.startTime} - {block.endTime}
                          </p>
                        </div>
                      </div>
                      <div className="text-sm text-muted-foreground">
                        {block.duration}m
                      </div>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {/* Today's Tasks */}
            <Card className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-accent" />
                Today's missions
              </h2>
              <div className="space-y-3">
                {loading ? (
                  <div className="text-center py-8 text-muted-foreground">Loading tasks...</div>
                ) : tasks.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">No tasks yet. Add one to get started!</div>
                ) : (
                  tasks.map((item, i) => (
                    <div
                      key={item.id || i}
                      className={`flex items-center justify-between p-4 rounded-xl border transition-all ${item.done
                        ? "bg-accent/10 border-accent/30"
                        : "bg-muted/30 border-border/50 hover:border-accent/50"
                        }`}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        {item.done ? (
                          <CheckCircle2 className="w-5 h-5 text-accent" />
                        ) : (
                          <div className="w-5 h-5 rounded-full border-2 border-muted-foreground" />
                        )}
                        <span className={item.done ? "line-through text-muted-foreground" : "font-medium"}>
                          {item.task}
                        </span>
                      </div>
                      <div className="flex items-center gap-2">
                        <div className="flex items-center gap-2 text-sm text-muted-foreground">
                          <Clock className="w-4 h-4" />
                          {item.time}
                        </div>
                        {!item.done && (
                          <div className="flex items-center gap-2 ml-4">
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={async () => {
                                try {
                                  await toggleTask(item.id)
                                  await loadTasks()
                                  await calculateStats() // Recalculate stats after task completion
                                  toast({
                                    title: "Task completed",
                                    description: "Task marked as done",
                                  })
                                } catch (error) {
                                  toast({
                                    title: "Error",
                                    description: error.message,
                                    variant: "destructive",
                                  })
                                }
                              }}
                              className="h-8"
                            >
                              Done
                            </Button>
                          </div>
                        )}
                      </div>
                    </div>
                  ))
                )}
              </div>
              <div className="flex gap-2 mt-4">
                <Button
                  variant="outline"
                  className="flex-1 bg-transparent"
                  onClick={() => setIsAddTaskOpen(true)}
                >
                  Add new task
                </Button>
                <Button
                  variant="default"
                  className="flex-1 bg-accent text-accent-foreground hover:bg-accent/90"
                  onClick={() => setIsEndDayOpen(true)}
                >
                  <Moon className="w-4 h-4 mr-2" />
                  End Day
                </Button>
              </div>
            </Card>

            {/* Add Task Dialog */}
            <Dialog open={isAddTaskOpen} onOpenChange={setIsAddTaskOpen}>
              <DialogContent className="max-w-2xl">
                <DialogHeader>
                  <DialogTitle>Add New Task</DialogTitle>
                  <DialogDescription>
                    Create a new task with all the details to help you stay organized.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-2">
                    <Label htmlFor="task-name">Task Name</Label>
                    <Textarea
                      id="task-name"
                      placeholder="What do you need to do?"
                      value={taskForm.name}
                      onChange={(e) => setTaskForm({ ...taskForm, name: e.target.value })}
                      className="min-h-20"
                    />
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="priority">Priority</Label>
                      <Select
                        value={taskForm.priority}
                        onValueChange={(value) => setTaskForm({ ...taskForm, priority: value })}
                      >
                        <SelectTrigger id="priority">
                          <SelectValue placeholder="Select priority" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="low">Low</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="high">High</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="difficulty">Difficulty Level</Label>
                      <Select
                        value={taskForm.difficulty}
                        onValueChange={(value) => setTaskForm({ ...taskForm, difficulty: value })}
                      >
                        <SelectTrigger id="difficulty">
                          <SelectValue placeholder="Select difficulty" />
                        </SelectTrigger>
                        <SelectContent>
                          <SelectItem value="easy">Easy</SelectItem>
                          <SelectItem value="medium">Medium</SelectItem>
                          <SelectItem value="hard">Hard</SelectItem>
                        </SelectContent>
                      </Select>
                    </div>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="space-y-2">
                      <Label htmlFor="estimated-time">Estimated Time (minutes)</Label>
                      <Input
                        id="estimated-time"
                        type="number"
                        min="1"
                        placeholder="e.g., 30"
                        value={taskForm.estimatedTime}
                        onChange={(e) => setTaskForm({ ...taskForm, estimatedTime: e.target.value })}
                      />
                    </div>

                    <div className="space-y-2">
                      <Label htmlFor="deadline">Deadline</Label>
                      <Popover>
                        <PopoverTrigger asChild>
                          <Button
                            id="deadline"
                            variant="outline"
                            className="w-full justify-start text-left font-normal"
                          >
                            <CalendarIcon className="mr-2 h-4 w-4" />
                            {taskForm.deadline ? format(taskForm.deadline, "PPP") : "Pick a date"}
                          </Button>
                        </PopoverTrigger>
                        <PopoverContent className="w-auto p-0" align="start">
                          <Calendar
                            mode="single"
                            selected={taskForm.deadline}
                            onSelect={(date) => setTaskForm({ ...taskForm, deadline: date })}
                            initialFocus
                          />
                        </PopoverContent>
                      </Popover>
                    </div>
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => setIsAddTaskOpen(false)}>
                    Cancel
                  </Button>
                  <Button
                    onClick={async () => {
                      if (taskForm.name.trim() && taskForm.estimatedTime) {
                        try {
                          await createTask({
                            name: taskForm.name,
                            estimatedTime: taskForm.estimatedTime,
                            difficulty: taskForm.difficulty || 'medium',
                          })
                          await loadTasks()
                          setTaskForm({
                            name: "",
                            priority: "",
                            difficulty: "",
                            estimatedTime: "",
                            deadline: null,
                          })
                          setIsAddTaskOpen(false)
                          toast({
                            title: "Task created",
                            description: "Task has been added successfully",
                          })
                        } catch (error) {
                          toast({
                            title: "Error creating task",
                            description: error.message,
                            variant: "destructive",
                          })
                        }
                      }
                    }}
                    className="bg-accent text-accent-foreground hover:bg-accent/90"
                    disabled={!taskForm.name.trim() || !taskForm.estimatedTime}
                  >
                    Add Task
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>

            {/* End Day Dialog */}
            <Dialog open={isEndDayOpen} onOpenChange={setIsEndDayOpen}>
              <DialogContent className="max-w-2xl max-h-[90vh] overflow-y-auto">
                <DialogHeader>
                  <div className="flex items-center gap-3 mb-2">
                    <Moon className="w-6 h-6 text-accent" />
                    <DialogTitle className="text-2xl">Day Complete</DialogTitle>
                  </div>
                  <DialogDescription className="text-base">
                    You completed {stats.tasksCompleted} of {stats.totalTasks} tasks
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-6 py-4">
                  {/* Mood Slider */}
                  <div className="space-y-4">
                    <Label className="text-base font-semibold">How did today feel?</Label>
                    <div className="space-y-3">
                      <div className="flex items-center gap-2">
                        <span className="text-sm text-muted-foreground">Drained</span>
                        <input
                          type="range"
                          min="1"
                          max="5"
                          value={endDayMood}
                          onChange={(e) => setEndDayMood(Number.parseInt(e.target.value))}
                          className="flex-1 h-2 bg-muted rounded-lg appearance-none cursor-pointer accent-accent"
                        />
                        <span className="text-sm text-muted-foreground">Energized</span>
                      </div>
                      <div className="flex items-center justify-between px-2">
                        {[1, 2, 3, 4, 5].map((value) => (
                          <button
                            key={value}
                            onClick={() => setEndDayMood(value)}
                            className={`text-3xl transition-transform ${endDayMood === value ? "scale-125" : "opacity-50 hover:opacity-75"
                              }`}
                          >
                            {value === 1 && "😡"}
                            {value === 2 && "😓"}
                            {value === 3 && "😐"}
                            {value === 4 && "😊"}
                            {value === 5 && "🔥"}
                          </button>
                        ))}
                      </div>
                    </div>
                  </div>

                  {/* Distractions */}
                  <div className="space-y-3">
                    <Label className="text-base font-semibold">What got in the way?</Label>
                    <div className="grid grid-cols-2 gap-2">
                      {[
                        { id: "meetings", label: "Meetings", icon: CalendarIcon },
                        { id: "fatigue", label: "Fatigue", icon: AlertCircle },
                        { id: "notifications", label: "Notifications", icon: Bell },
                        { id: "ad-hoc", label: "Ad-hoc requests", icon: Users },
                        { id: "personal", label: "Personal", icon: Home },
                        { id: "unclear-priorities", label: "Unclear priorities", icon: HelpCircle },
                      ].map((distraction) => {
                        const isSelected = selectedDistractions.includes(distraction.id)
                        const Icon = distraction.icon
                        return (
                          <button
                            key={distraction.id}
                            onClick={() => {
                              if (isSelected) {
                                setSelectedDistractions(selectedDistractions.filter(d => d !== distraction.id))
                              } else {
                                setSelectedDistractions([...selectedDistractions, distraction.id])
                              }
                            }}
                            className={`flex items-center gap-2 p-3 rounded-lg border transition-all ${isSelected
                              ? "border-accent bg-accent/10"
                              : "border-border/50 hover:border-accent/50"
                              }`}
                          >
                            <Icon className={`w-4 h-4 ${isSelected ? "text-accent" : "text-muted-foreground"}`} />
                            <span className={`text-sm ${isSelected ? "font-medium" : ""}`}>{distraction.label}</span>
                          </button>
                        )
                      })}
                    </div>
                  </div>

                  {/* Notes */}
                  <div className="space-y-2">
                    <Label htmlFor="end-day-note" className="text-base font-semibold">Anything to note?</Label>
                    <Textarea
                      id="end-day-note"
                      placeholder="Optional thoughts about today..."
                      value={endDayNote}
                      onChange={(e) => setEndDayNote(e.target.value)}
                      className="min-h-24 resize-none"
                    />
                  </div>
                </div>
                <DialogFooter>
                  <Button
                    variant="outline"
                    onClick={() => {
                      setIsEndDayOpen(false)
                      setEndDayMood(3)
                      setSelectedDistractions([])
                      setEndDayNote("")
                    }}
                  >
                    Skip
                  </Button>
                  <Button
                    onClick={async () => {
                      setSubmittingEndDay(true)
                      try {
                        const completedTasks = tasks.filter(t => t.completed).length
                        const totalTasks = tasks.length

                        await createReflection({
                          mood: endDayMood,
                          moodScore: endDayMood,
                          note: endDayNote,
                          reflection: endDayNote,
                          distractions: selectedDistractions,
                          completedTasks: completedTasks,
                          totalTasks: totalTasks,
                        })

                        toast({
                          title: "Day completed!",
                          description: "Your reflection has been saved. Great work today! 🎉",
                        })

                        // Refresh stats and close dialog
                        await loadTodayReflection()
                        await calculateStats()
                        setIsEndDayOpen(false)
                        setEndDayMood(3)
                        setSelectedDistractions([])
                        setEndDayNote("")

                        // Trigger event for streak update
                        window.dispatchEvent(new Event('reflectionSubmitted'))
                      } catch (error) {
                        toast({
                          title: "Error saving reflection",
                          description: error.message,
                          variant: "destructive",
                        })
                      } finally {
                        setSubmittingEndDay(false)
                      }
                    }}
                    className="bg-accent text-accent-foreground hover:bg-accent/90"
                    disabled={submittingEndDay}
                  >
                    {submittingEndDay ? "Saving..." : "Save & Close Day"}
                  </Button>
                </DialogFooter>
              </DialogContent>
            </Dialog>
          </div>

          {/* Sidebar - Stats & Info */}
          <div className="space-y-6">
            {/* Streak Card */}
            <Card className="p-6 bg-gradient-to-br from-chart-1/10 to-chart-2/10 border-chart-1/30">
              <div className="flex items-center justify-between mb-4">
                <h3 className="font-bold">Current Streak</h3>
                <span className="text-3xl">🔥</span>
              </div>
              <div className="text-5xl font-bold mb-2">{stats.streak} {stats.streak === 1 ? 'day' : 'days'}</div>
              <p className="text-sm text-muted-foreground">
                {stats.streak === 0
                  ? "Start your streak by completing a check-in today!"
                  : stats.streak < 3
                    ? "Keep it going! You're building momentum 💪"
                    : stats.streak < 7
                      ? "You're on a roll! Keep it going bestie"
                      : "Incredible streak! You're unstoppable 🔥"}
              </p>
            </Card>

            {/* Today's Stats */}
            <Card className="p-6">
              <h3 className="font-bold mb-4 flex items-center gap-2">
                <TrendingUp className="w-5 h-5 text-accent" />
                Today's stats
              </h3>
              <div className="space-y-4">
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Focus time</span>
                    <span className="font-bold">
                      {Math.floor(stats.focusTime / 60) > 0
                        ? `${Math.floor(stats.focusTime / 60)}h ${stats.focusTime % 60}min`
                        : `${stats.focusTime}min`}
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-accent rounded-full h-2"
                      style={{ width: `${Math.min(100, (stats.focusTime / stats.focusTimeGoal) * 100)}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Tasks completed</span>
                    <span className="font-bold">
                      {stats.totalTasks > 0 ? `${stats.tasksCompleted}/${stats.totalTasks}` : '0/0'}
                    </span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-chart-2 rounded-full h-2"
                      style={{ width: `${stats.totalTasks > 0 ? (stats.tasksCompleted / stats.totalTasks) * 100 : 0}%` }}
                    />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Distractions blocked</span>
                    <span className="font-bold">{stats.distractionsBlocked}</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div
                      className="bg-chart-4 rounded-full h-2"
                      style={{ width: `${Math.min(100, (stats.distractionsBlocked / Math.max(1, blockedAppsCount)) * 100)}%` }}
                    />
                  </div>
                </div>
              </div>
            </Card>

            {/* AI Coach Tip */}
            <Card className="p-6 bg-primary/5 border-primary/30">
              <div className="flex items-start gap-3">
                <div className="w-10 h-10 rounded-full bg-primary flex items-center justify-center flex-shrink-0">
                  <Sparkles className="w-5 h-5 text-primary-foreground" />
                </div>
                <div>
                  <h3 className="font-bold mb-2">Coach's tip</h3>
                  <p className="text-sm leading-relaxed text-muted-foreground">
                    {stats.tasksCompleted === 0 && stats.totalTasks > 0
                      ? "Start with your easiest task to build momentum! 🚀"
                      : stats.tasksCompleted === stats.totalTasks && stats.totalTasks > 0
                        ? "Amazing! You've completed all your tasks today! 🎉"
                        : stats.tasksCompleted / stats.totalTasks < 0.5 && stats.totalTasks > 0
                          ? "You're making progress! Try focusing on one task at a time 💪"
                          : stats.focusTime < 60
                            ? "Build your focus time gradually. Start with 25-minute sessions! ⏱️"
                            : schedule.length > 0
                              ? "Your schedule is set! Follow it to maximize productivity 🎯"
                              : "Create a schedule to organize your day better! 📅"}
                  </p>
                </div>
              </div>
            </Card>

            {/* Break Reminder */}
            {stats.focusTime > 0 && (
              <Card className="p-6 bg-chart-3/5 border-chart-3/30">
                <div className="text-center">
                  <Coffee className="w-12 h-12 mx-auto mb-3 text-chart-3" />
                  <h3 className="font-bold mb-2">Time for a break?</h3>
                  <p className="text-sm text-muted-foreground mb-4">
                    {stats.focusTime >= 120
                      ? `You've been grinding for ${Math.floor(stats.focusTime / 60)} hours straight`
                      : stats.focusTime >= 60
                        ? `You've been working for over an hour`
                        : `You've been focused for ${stats.focusTime} minutes`}
                  </p>
                  <Button
                    size="sm"
                    className="w-full"
                    onClick={() => {
                      setIsInSession(false)
                      toast({
                        title: "Break time!",
                        description: "Take a well-deserved rest ☕",
                      })
                    }}
                  >
                    Take 5 minutes
                  </Button>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  )
}
