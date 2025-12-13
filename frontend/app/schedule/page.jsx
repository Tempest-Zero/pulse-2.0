"use client"

import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
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
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Popover, PopoverContent, PopoverTrigger } from "@/components/ui/popover"
import { Calendar as CalendarComponent } from "@/components/ui/calendar"
import { format } from "date-fns"
import { Calendar, Clock, Sparkles, Plus, Trash2, Zap, CalendarIcon, MessageSquare, CheckCircle2 } from "lucide-react"
import { useState } from "react"
import { useTasks, useCreateTask, useDeleteTask, useToggleTask } from "@/hooks"

export default function SchedulePage() {
  // React Query hooks for tasks
  const { data: tasks = [], isLoading: isLoadingTasks } = useTasks()
  const createTaskMutation = useCreateTask()
  const deleteTaskMutation = useDeleteTask()
  const toggleTaskMutation = useToggleTask()

  const [newTask, setNewTask] = useState("")
  const [duration, setDuration] = useState(60)
  const [schedule, setSchedule] = useState([])
  const [generating, setGenerating] = useState(false)
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false)
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

  const addTask = () => {
    if (taskForm.name.trim() && taskForm.estimatedTime) {
      createTaskMutation.mutate({
        title: taskForm.name,
        durationMinutes: Number.parseInt(taskForm.estimatedTime),
        priority: taskForm.priority || 'medium',
        difficulty: taskForm.difficulty || 'medium',
      }, {
        onSuccess: () => {
          setTaskForm({
            name: "",
            priority: "",
            difficulty: "",
            estimatedTime: "",
            deadline: null,
          })
          setIsAddTaskOpen(false)
        }
      })
    }
  }

  const deleteTask = (id) => {
    deleteTaskMutation.mutate(id)
  }

  const generateSchedule = () => {
    setGenerating(true)

    // Simulate AI generation
    setTimeout(() => {
      const currentTime = new Date()
      currentTime.setHours(9, 0, 0, 0) // Start at 9 AM

      const generatedSchedule = tasks.map((task) => {
        const startTime = new Date(currentTime)
        currentTime.setMinutes(currentTime.getMinutes() + task.duration + 15) // Add 15 min break

        return {
          ...task,
          startTime: startTime.toLocaleTimeString("en-US", { hour: "numeric", minute: "2-digit" }),
          endTime: new Date(startTime.getTime() + task.duration * 60000).toLocaleTimeString("en-US", {
            hour: "numeric",
            minute: "2-digit",
          }),
          aiTip: getAITip(task.name),
        }
      })

      setSchedule(generatedSchedule)
      setGenerating(false)
    }, 2000)
  }

  const getAITip = (taskName) => {
    const tips = [
      "Use the Pomodoro technique for better focus",
      "Take a 5-min walk before starting this",
      "Put your phone in another room",
      "Play lofi beats to stay in the zone",
      "Grab a snack before diving in",
      "Set a timer so you don't lose track",
    ]
    return tips[Math.floor(Math.random() * tips.length)]
  }

  return (
    <div className="min-h-screen bg-background">
      <Navigation />

      <main className="container mx-auto px-4 py-8">
        <div className="mb-8">
          <h1 className="text-4xl md:text-5xl font-bold mb-4 text-balance">
            Daily <span className="text-accent">Schedule</span>
          </h1>
          <p className="text-muted-foreground text-lg">Let AI plan your perfect day based on your tasks</p>
        </div>

        <div className="grid lg:grid-cols-2 gap-6">
          {/* Task Input Section */}
          <Card className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Plus className="w-5 h-5 text-accent" />
                Your Tasks
              </CardTitle>
              <CardDescription>Add tasks and we'll optimize your schedule</CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              {/* Add Task Button */}
              <Button
                onClick={() => setIsAddTaskOpen(true)}
                className="w-full bg-accent hover:bg-accent/90"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Task
              </Button>

              {/* Task List */}
              <div className="space-y-2 mt-6">
                {tasks.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No tasks yet. Add some to get started!</p>
                  </div>
                ) : (
                  tasks.map((task) => (
                    <div
                      key={task.id}
                      className={`flex items-center justify-between p-3 rounded-lg border transition-all ${task.done
                        ? "bg-accent/10 border-accent/30"
                        : "bg-muted/50 border-border/50"
                        }`}
                    >
                      <div className="flex items-center gap-3 flex-1">
                        {task.done ? (
                          <CheckCircle2 className="w-5 h-5 text-accent" />
                        ) : (
                          <div className="w-5 h-5 rounded-full border-2 border-muted-foreground" />
                        )}
                        <div>
                          <p className={`font-medium ${task.done ? "line-through text-muted-foreground" : ""}`}>
                            {task.name}
                          </p>
                          <p className="text-sm text-muted-foreground flex items-center gap-1">
                            <Clock className="w-3 h-3" />
                            {task.duration} minutes
                          </p>
                        </div>
                      </div>
                      <div className="flex items-center gap-2">
                        {!task.done && (
                          <>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => toggleTaskMutation.mutate(task.id)}
                              disabled={toggleTaskMutation.isPending}
                              className="h-8"
                            >
                              {toggleTaskMutation.isPending ? "..." : "Done"}
                            </Button>
                            <Button
                              size="sm"
                              variant="outline"
                              onClick={() => {
                                setSelectedTaskId(task.id)
                                setIsReflectionOpen(true)
                              }}
                              className="h-8"
                            >
                              <MessageSquare className="w-4 h-4 mr-1" />
                              Reflection
                            </Button>
                          </>
                        )}
                        <Button variant="ghost" size="icon" onClick={() => deleteTask(task.id)}>
                          <Trash2 className="w-4 h-4 text-destructive" />
                        </Button>
                      </div>
                    </div>
                  ))
                )}
              </div>

              {/* Generate Button */}
              {tasks.length > 0 && (
                <Button
                  onClick={generateSchedule}
                  disabled={generating}
                  className="w-full bg-accent hover:bg-accent/90 mt-6"
                  size="lg"
                >
                  {generating ? (
                    <>
                      <Sparkles className="w-5 h-5 mr-2 animate-spin" />
                      Generating your perfect schedule...
                    </>
                  ) : (
                    <>
                      <Zap className="w-5 h-5 mr-2" />
                      Generate AI Schedule
                    </>
                  )}
                </Button>
              )}
            </CardContent>
          </Card>

          {/* Generated Schedule Section */}
          <Card className="border-border/50">
            <CardHeader>
              <CardTitle className="flex items-center gap-2">
                <Sparkles className="w-5 h-5 text-accent" />
                Your Optimized Schedule
              </CardTitle>
              <CardDescription>AI-generated timeline for maximum productivity</CardDescription>
            </CardHeader>
            <CardContent>
              {schedule.length === 0 ? (
                <div className="text-center py-12 text-muted-foreground">
                  <Sparkles className="w-16 h-16 mx-auto mb-3 opacity-30" />
                  <p className="text-lg mb-1">Schedule not generated yet</p>
                  <p className="text-sm">Add tasks and hit the generate button</p>
                </div>
              ) : (
                <div className="space-y-4">
                  {schedule.map((item, index) => (
                    <div
                      key={item.id}
                      className="relative p-4 rounded-lg bg-accent/10 border-l-4 border-accent hover:bg-accent/15 transition-colors"
                    >
                      <div className="flex items-start justify-between mb-2">
                        <div>
                          <p className="font-semibold text-lg">{item.name}</p>
                          <p className="text-sm text-muted-foreground flex items-center gap-2 mt-1">
                            <Clock className="w-3 h-3" />
                            {item.startTime} - {item.endTime}
                          </p>
                        </div>
                        <div className="text-xs font-medium text-accent bg-accent/20 px-2 py-1 rounded">
                          {item.duration}m
                        </div>
                      </div>
                      <div className="mt-3 p-2 rounded bg-muted/50 border border-border/30">
                        <p className="text-xs text-muted-foreground flex items-start gap-2">
                          <Sparkles className="w-3 h-3 text-accent mt-0.5 flex-shrink-0" />
                          <span>
                            <strong>AI Tip:</strong> {item.aiTip}
                          </span>
                        </p>
                      </div>
                      {index < schedule.length - 1 && (
                        <div className="absolute -bottom-2 left-1/2 -translate-x-1/2 text-xs bg-background px-2 text-muted-foreground">
                          15 min break
                        </div>
                      )}
                    </div>
                  ))}
                  <div className="mt-6 p-4 rounded-lg bg-muted/30 border border-border/50">
                    <p className="text-sm text-center text-muted-foreground">
                      Total time:{" "}
                      <strong className="text-foreground">
                        {schedule.reduce((acc, item) => acc + item.duration, 0)} minutes
                      </strong>{" "}
                      + breaks
                    </p>
                  </div>
                </div>
              )}
            </CardContent>
          </Card>
        </div>

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
                      <CalendarComponent
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
                    addTask()
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
                    className={`w-full text-left p-3 rounded-lg border transition-all ${reflectionReason === option.value
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
      </main>
    </div>
  )
}
