"use client"

import { useState, useEffect } from "react"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { getTasks, createTask, deleteTask, transformTask } from "@/lib/api/tasks"
import { getScheduleBlocks, createScheduleBlock, clearAllScheduleBlocks, transformScheduleBlock, uploadClassSchedule, getAvailableSlots, deleteScheduleBlock } from "@/lib/api/schedule"
import { breakdownTask } from "@/lib/api/ai"
import { useToast } from "@/hooks/use-toast"
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
import { Calendar, Clock, Sparkles, Plus, Trash2, Zap, CalendarIcon, MessageSquare, CheckCircle2, Upload, Scissors, ChevronDown, ChevronRight } from "lucide-react"

export default function SchedulePage() {
  const { toast } = useToast()
  const [tasks, setTasks] = useState([])
  const [newTask, setNewTask] = useState("")
  const [duration, setDuration] = useState(60)
  const [schedule, setSchedule] = useState([])
  const [generating, setGenerating] = useState(false)
  const [loading, setLoading] = useState(true)
  const [isAddTaskOpen, setIsAddTaskOpen] = useState(false)
  const [taskForm, setTaskForm] = useState({
    name: "",
    description: "",
    priority: "",
    difficulty: "",
    estimatedTime: "",
    deadline: null,
  })
  const [expandedTasks, setExpandedTasks] = useState(new Set())
  const [breakingDown, setBreakingDown] = useState(new Set())
  const [classScheduleOpen, setClassScheduleOpen] = useState(false)
  const [uploadingSchedule, setUploadingSchedule] = useState(false)
  const [newClassBlock, setNewClassBlock] = useState({ title: "", start: "", duration: "" })
  const [isReflectionOpen, setIsReflectionOpen] = useState(false)
  const [selectedTaskId, setSelectedTaskId] = useState(null)
  const [reflectionReason, setReflectionReason] = useState("")

  // Load tasks and schedule on mount
  useEffect(() => {
    loadTasks()
    loadSchedule()
  }, [])

  const loadTasks = async () => {
    try {
      setLoading(true)
      const data = await getTasks(false) // Get incomplete tasks
      const transformed = data.map(transformTask)
      
      // Load subtasks for each task
      for (const task of transformed) {
        const subtasks = data.filter(t => t.parentId === task.id || t.parent_id === task.id)
        task.subtasks = subtasks.map(transformTask)
      }
      
      setTasks(transformed.filter(t => !t.parentId && !t.parent_id)) // Only show parent tasks
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
  
  const handleBreakdown = async (taskId) => {
    try {
      setBreakingDown(prev => new Set(prev).add(taskId))
      const result = await breakdownTask(taskId)
      await loadTasks()
      toast({
        title: "Task broken down",
        description: result.message,
      })
    } catch (error) {
      toast({
        title: "Error breaking down task",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setBreakingDown(prev => {
        const newSet = new Set(prev)
        newSet.delete(taskId)
        return newSet
      })
    }
  }
  
  const toggleTaskExpansion = (taskId) => {
    setExpandedTasks(prev => {
      const newSet = new Set(prev)
      if (newSet.has(taskId)) {
        newSet.delete(taskId)
      } else {
        newSet.add(taskId)
      }
      return newSet
    })
  }

  const loadSchedule = async () => {
    try {
      const data = await getScheduleBlocks()
      setSchedule(data.map(transformScheduleBlock))
    } catch (error) {
      console.log('No schedule blocks yet')
    }
  }

  const handleDeleteTask = async (id) => {
    try {
      await deleteTask(id)
      await loadTasks()
      toast({
        title: "Task deleted",
        description: "Task has been removed",
      })
    } catch (error) {
      toast({
        title: "Error deleting task",
        description: error.message,
        variant: "destructive",
      })
    }
  }

  const generateSchedule = async () => {
    if (tasks.length === 0) {
      toast({
        title: "No tasks",
        description: "Add some tasks first to generate a schedule",
        variant: "destructive",
      })
      return
    }

    setGenerating(true)

    try {
      // Clear existing task schedule blocks (keep fixed ones)
      const existingBlocks = await getScheduleBlocks()
      for (const block of existingBlocks) {
        if (block.block_type === 'task') {
          await deleteScheduleBlock(block.id)
        }
      }

      // Get all tasks including subtasks
      const allTasks = []
      for (const task of tasks) {
        if (task.subtasks && task.subtasks.length > 0) {
          // Use subtasks instead of parent
          allTasks.push(...task.subtasks)
        } else {
          allTasks.push(task)
        }
      }

      // Get available slots
      const availableSlots = await getAvailableSlots(9.0, 20.0, 1.0)
      
      let slotIndex = 0
      const newSchedule = []

      for (const task of allTasks) {
        const taskDurationHours = task.duration / 60
        
        // Find next available slot
        let scheduled = false
        while (slotIndex < availableSlots.available_slots.length && !scheduled) {
          const slot = availableSlots.available_slots[slotIndex]
          if (slot.duration >= taskDurationHours) {
            // Create schedule block for this task
            const blockData = {
              title: task.task || task.name,
              start: slot.start,
              duration: taskDurationHours,
              block_type: 'task',
            }

            const createdBlock = await createScheduleBlock(blockData)
            const transformed = transformScheduleBlock(createdBlock)
            transformed.aiTip = getAITip(task.task || task.name)
            newSchedule.push(transformed)
            scheduled = true
          }
          slotIndex++
        }
        
        if (!scheduled) {
          toast({
            title: "Warning",
            description: `Could not schedule "${task.name}" - no available slots`,
            variant: "destructive",
          })
        }
      }

      await loadSchedule()
      toast({
        title: "Schedule generated",
        description: "Your schedule has been created successfully",
      })
    } catch (error) {
      toast({
        title: "Error generating schedule",
        description: error.message,
        variant: "destructive",
      })
    } finally {
      setGenerating(false)
    }
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

        {/* Class Schedule Section */}
        <Card className="mb-6 border-border/50">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <Calendar className="w-5 h-5 text-accent" />
              Class Schedule
            </CardTitle>
            <CardDescription>
              Upload your class schedule or enter times manually so AI avoids conflicts
            </CardDescription>
          </CardHeader>
          <CardContent className="space-y-4">
            <div className="flex gap-4">
              <div className="flex-1">
                <Label htmlFor="schedule-upload">Upload Schedule Image</Label>
                <div className="mt-2 flex items-center gap-2">
                  <Input
                    id="schedule-upload"
                    type="file"
                    accept="image/*"
                    onChange={async (e) => {
                      const file = e.target.files?.[0]
                      if (file) {
                        try {
                          setUploadingSchedule(true)
                          const result = await uploadClassSchedule(file)
                          toast({
                            title: "Image uploaded",
                            description: result.message,
                          })
                        } catch (error) {
                          toast({
                            title: "Upload failed",
                            description: error.message,
                            variant: "destructive",
                          })
                        } finally {
                          setUploadingSchedule(false)
                        }
                      }
                    }}
                    disabled={uploadingSchedule}
                    className="cursor-pointer"
                  />
                </div>
              </div>
              <Button
                variant="outline"
                onClick={() => setClassScheduleOpen(true)}
                className="mt-8"
              >
                <Plus className="w-4 h-4 mr-2" />
                Add Manually
              </Button>
            </div>
          </CardContent>
        </Card>

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
                {loading ? (
                  <div className="text-center py-8 text-muted-foreground">Loading tasks...</div>
                ) : tasks.length === 0 ? (
                  <div className="text-center py-8 text-muted-foreground">
                    <Calendar className="w-12 h-12 mx-auto mb-2 opacity-50" />
                    <p>No tasks yet. Add some to get started!</p>
                  </div>
                ) : (
                  tasks.map((task) => (
                    <div key={task.id}>
                      <div
                        className={`flex items-center justify-between p-3 rounded-lg border transition-all ${
                          task.done
                            ? "bg-accent/10 border-accent/30"
                            : "bg-muted/50 border-border/50"
                        }`}
                      >
                        <div className="flex items-center gap-3 flex-1">
                          {task.subtasks && task.subtasks.length > 0 && (
                            <button
                              onClick={() => toggleTaskExpansion(task.id)}
                              className="p-1 hover:bg-muted rounded"
                            >
                              {expandedTasks.has(task.id) ? (
                                <ChevronDown className="w-4 h-4" />
                              ) : (
                                <ChevronRight className="w-4 h-4" />
                              )}
                            </button>
                          )}
                          {task.done ? (
                            <CheckCircle2 className="w-5 h-5 text-accent" />
                          ) : (
                            <div className="w-5 h-5 rounded-full border-2 border-muted-foreground" />
                          )}
                          <div className="flex-1">
                            <p className={`font-medium ${task.done ? "line-through text-muted-foreground" : ""}`}>
                              {task.name}
                            </p>
                            <p className="text-sm text-muted-foreground flex items-center gap-1">
                              <Clock className="w-3 h-3" />
                              {task.duration} minutes
                              {task.subtasks && task.subtasks.length > 0 && (
                                <> • {task.subtasks.length} subtasks</>
                              )}
                            </p>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          {!task.done && (
                            <>
                              {!task.subtasks || task.subtasks.length === 0 ? (
                                <Button
                                  size="sm"
                                  variant="outline"
                                  onClick={() => handleBreakdown(task.id)}
                                  disabled={breakingDown.has(task.id)}
                                  className="h-8"
                                >
                                  <Scissors className="w-4 h-4 mr-1" />
                                  {breakingDown.has(task.id) ? "Breaking..." : "Break Down"}
                                </Button>
                              ) : null}
                              <Button
                                size="sm"
                                variant="outline"
                                onClick={() => {
                                  setTasks(tasks.map((t) => (t.id === task.id ? { ...t, done: true } : t)))
                                }}
                                className="h-8"
                              >
                                Done
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
                          <Button variant="ghost" size="icon" onClick={() => handleDeleteTask(task.id)}>
                            <Trash2 className="w-4 h-4 text-destructive" />
                          </Button>
                        </div>
                      </div>
                      {expandedTasks.has(task.id) && task.subtasks && task.subtasks.length > 0 && (
                        <div className="ml-8 mt-2 space-y-2">
                          {task.subtasks.map((subtask) => (
                            <div
                              key={subtask.id}
                              className="flex items-center justify-between p-2 rounded-lg border border-border/50 bg-muted/30"
                            >
                              <div className="flex items-center gap-2 flex-1">
                                <div className="w-4 h-4 rounded-full border border-muted-foreground" />
                                <span className="text-sm">{subtask.name}</span>
                                <span className="text-xs text-muted-foreground">
                                  {subtask.duration} min
                                </span>
                              </div>
                            </div>
                          ))}
                        </div>
                      )}
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
                <Input
                  id="task-name"
                  placeholder="What do you need to do?"
                  value={taskForm.name}
                  onChange={(e) => setTaskForm({ ...taskForm, name: e.target.value })}
                />
              </div>
              
              <div className="space-y-2">
                <Label htmlFor="task-description">Description (for AI breakdown)</Label>
                <Textarea
                  id="task-description"
                  placeholder="Describe the task in detail. The AI will use this to break it down into manageable subtasks..."
                  value={taskForm.description}
                  onChange={(e) => setTaskForm({ ...taskForm, description: e.target.value })}
                  className="min-h-24"
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
                onClick={async () => {
                  if (taskForm.name.trim() && taskForm.estimatedTime) {
                    try {
                      await createTask({
                        name: taskForm.name,
                        description: taskForm.description,
                        estimatedTime: taskForm.estimatedTime,
                        difficulty: taskForm.difficulty || 'medium',
                      })
                      await loadTasks()
                      setTaskForm({
                        name: "",
                        description: "",
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
      </main>
    </div>
  )
}
