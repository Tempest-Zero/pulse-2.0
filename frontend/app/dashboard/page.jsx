"use client"

import { useState } from "react"
import { Button } from "@/components/ui/button"
import { Card } from "@/components/ui/card"
import { Navigation } from "@/components/navigation"
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
  MessageSquare,
} from "lucide-react"

export default function DashboardPage() {
  const [isInSession, setIsInSession] = useState(false)
  const [sessionTime, setSessionTime] = useState(25 * 60)
  const [mood, setMood] = useState(null)
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false)
  const [tasks, setTasks] = useState([
    { id: 1, task: "Finish project proposal", done: true, time: "45 min" },
    { id: 2, task: "Study for exam", done: true, time: "1h 20min" },
    { id: 3, task: "Review pull requests", done: false, time: "30 min" },
    { id: 4, task: "Gym session", done: false, time: "1h" },
  ])
  const [taskForm, setTaskForm] = useState({
    name: "",
    priority: "",
    difficulty: "",
    estimatedTime: "",
    deadline: null,
  })
  const [isReflectionOpen, setIsReflectionOpen] = useState(false)
  const [selectedTaskId, setSelectedTaskId] = useState(null)
  const [reflectionReason, setReflectionReason] = useState("")

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
                onClick={() => setMood(m.value)}
                className={`flex flex-col items-center gap-2 p-4 rounded-2xl border-2 transition-all ${
                  mood === m.value
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
                    onClick={() => setIsInSession(!isInSession)}
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
                  <Button variant="outline" size="lg" className="rounded-2xl bg-transparent">
                    <SkipForward className="w-5 h-5 mr-2" />
                    Skip to Break
                  </Button>
                </div>

                <div className="flex items-center justify-center gap-2 text-sm text-muted-foreground">
                  <Shield className="w-4 h-4" />
                  <span>7 distracting apps blocked</span>
                </div>
              </div>
            </Card>

            {/* Today's Tasks */}
            <Card className="p-6">
              <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                <CheckCircle2 className="w-5 h-5 text-accent" />
                Today's missions
              </h2>
              <div className="space-y-3">
                {tasks.map((item, i) => (
                  <div
                    key={i}
                    className={`flex items-center justify-between p-4 rounded-xl border transition-all ${
                      item.done
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
                            onClick={() => {
                              setTasks(tasks.map((t) => (t.id === item.id ? { ...t, done: true } : t)))
                            }}
                            className="h-8"
                          >
                            Done
                          </Button>
                          <Button
                            size="sm"
                            variant="outline"
                            onClick={() => {
                              setSelectedTaskId(item.id)
                              setIsReflectionOpen(true)
                            }}
                            className="h-8"
                          >
                            <MessageSquare className="w-4 h-4 mr-1" />
                            Reflection
                          </Button>
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
              <Button
                variant="outline"
                className="w-full mt-4 bg-transparent"
                onClick={() => setIsAddTaskOpen(true)}
              >
                Add new task
              </Button>
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
                    onClick={() => {
                      if (taskForm.name.trim() && taskForm.estimatedTime) {
                        const timeStr =
                          Number.parseInt(taskForm.estimatedTime) >= 60
                            ? `${Math.floor(Number.parseInt(taskForm.estimatedTime) / 60)}h ${
                                Number.parseInt(taskForm.estimatedTime) % 60
                                  ? `${Number.parseInt(taskForm.estimatedTime) % 60} min`
                                  : ""
                              }`.trim()
                            : `${taskForm.estimatedTime} min`

                        setTasks([
                          ...tasks,
                          {
                            id: Date.now(),
                            task: taskForm.name,
                            done: false,
                            time: timeStr,
                            priority: taskForm.priority,
                            difficulty: taskForm.difficulty,
                            deadline: taskForm.deadline,
                          },
                        ])
                        setTaskForm({
                          name: "",
                          priority: "",
                          difficulty: "",
                          estimatedTime: "",
                          deadline: null,
                        })
                        setIsAddTaskOpen(false)
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

            {/* Reflection Dialog */}
            <Dialog open={isReflectionOpen} onOpenChange={setIsReflectionOpen}>
              <DialogContent>
                <DialogHeader>
                  <DialogTitle>Why couldn't you complete this task?</DialogTitle>
                  <DialogDescription>
                    Understanding what got in the way helps us improve your schedule.
                  </DialogDescription>
                </DialogHeader>
                <div className="space-y-4 py-4">
                  <div className="space-y-3">
                    {[
                      { value: "too-difficult", label: "It was too difficult" },
                      { value: "not-enough-time", label: "Didn't have enough time" },
                      { value: "distracted", label: "Got distracted" },
                      { value: "low-energy", label: "Low energy/motivation" },
                      { value: "unclear-requirements", label: "Unclear requirements" },
                      { value: "other-priority", label: "Other priority came up" },
                      { value: "technical-issue", label: "Technical issue" },
                    ].map((option) => (
                      <button
                        key={option.value}
                        onClick={() => setReflectionReason(option.value)}
                        className={`w-full text-left p-3 rounded-lg border transition-all ${
                          reflectionReason === option.value
                            ? "border-accent bg-accent/10"
                            : "border-border/50 hover:border-accent/50"
                        }`}
                      >
                        {option.label}
                      </button>
                    ))}
                  </div>
                </div>
                <DialogFooter>
                  <Button variant="outline" onClick={() => {
                    setIsReflectionOpen(false)
                    setReflectionReason("")
                    setSelectedTaskId(null)
                  }}>
                    Cancel
                  </Button>
                  <Button
                    onClick={() => {
                      if (reflectionReason) {
                        console.log("Reflection submitted:", {
                          taskId: selectedTaskId,
                          reason: reflectionReason,
                        })
                        // You can add logic here to save the reflection
                        setIsReflectionOpen(false)
                        setReflectionReason("")
                        setSelectedTaskId(null)
                      }
                    }}
                    className="bg-accent text-accent-foreground hover:bg-accent/90"
                    disabled={!reflectionReason}
                  >
                    Submit
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
              <div className="text-5xl font-bold mb-2">12 days</div>
              <p className="text-sm text-muted-foreground">You're on a roll! Keep it going bestie</p>
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
                    <span className="font-bold">2h 5min</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-accent rounded-full h-2" style={{ width: "65%" }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Tasks completed</span>
                    <span className="font-bold">2/4</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-chart-2 rounded-full h-2" style={{ width: "50%" }} />
                  </div>
                </div>
                <div>
                  <div className="flex items-center justify-between mb-2">
                    <span className="text-sm text-muted-foreground">Distractions blocked</span>
                    <span className="font-bold">23</span>
                  </div>
                  <div className="w-full bg-muted rounded-full h-2">
                    <div className="bg-chart-4 rounded-full h-2" style={{ width: "85%" }} />
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
                    You tend to focus better after 2pm. I've scheduled your heavy tasks for later today 🎯
                  </p>
                </div>
              </div>
            </Card>

            {/* Break Reminder */}
            <Card className="p-6 bg-chart-3/5 border-chart-3/30">
              <div className="text-center">
                <Coffee className="w-12 h-12 mx-auto mb-3 text-chart-3" />
                <h3 className="font-bold mb-2">Time for a break?</h3>
                <p className="text-sm text-muted-foreground mb-4">You've been grinding for 2 hours straight</p>
                <Button size="sm" className="w-full">
                  Take 5 minutes
                </Button>
              </div>
            </Card>
          </div>
        </div>
      </div>
    </div>
  )
}
