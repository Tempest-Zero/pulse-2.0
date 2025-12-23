"use client"

import { useState } from "react"
import { Navigation } from "@/components/navigation"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { Clock, Sparkles, FileText, Wand2, Brain, Lightbulb, AlertCircle } from "lucide-react"
import { generateSmartSchedule, transformScheduledTask } from "@/lib/api/smart-schedule"

export default function SmartSchedulePage() {
    const { toast } = useToast()
    const [taskDescription, setTaskDescription] = useState("")
    const [schedule, setSchedule] = useState([])
    const [generating, setGenerating] = useState(false)
    const [error, setError] = useState(null)
    const [scheduleInfo, setScheduleInfo] = useState(null)

    const handleGenerateSchedule = async () => {
        if (!taskDescription.trim()) {
            toast({
                title: "No description",
                description: "Please describe your tasks first",
                variant: "destructive",
            })
            return
        }

        setGenerating(true)
        setError(null)

        try {
            const response = await generateSmartSchedule(taskDescription, {
                startHour: 9,
                endHour: 20,
                breakDuration: 15,
            })

            if (response.success && response.scheduled_tasks?.length > 0) {
                const transformedTasks = response.scheduled_tasks.map(transformScheduledTask)
                setSchedule(transformedTasks)
                setScheduleInfo({
                    tasksFound: response.tasks_found,
                    totalDuration: response.total_duration,
                    schedulingWindow: response.scheduling_window,
                })

                toast({
                    title: "Schedule generated! ✨",
                    description: response.message,
                })
            } else {
                setSchedule([])
                setError(response.message || "Could not generate schedule")
                toast({
                    title: "Schedule generation failed",
                    description: response.message,
                    variant: "destructive",
                })
            }
        } catch (err) {
            setError(err.message || "Failed to connect to the server")
            toast({
                title: "Error",
                description: err.message || "Failed to generate schedule",
                variant: "destructive",
            })
        } finally {
            setGenerating(false)
        }
    }

    const clearAll = () => {
        setTaskDescription("")
        setSchedule([])
        setError(null)
        setScheduleInfo(null)
    }

    return (
        <div className="min-h-screen bg-background">
            <Navigation />

            <main className="container mx-auto px-4 py-8">
                <div className="mb-8">
                    <h1 className="text-4xl md:text-5xl font-bold mb-4 text-balance">
                        Smart <span className="text-accent">Schedule</span>
                    </h1>
                    <p className="text-muted-foreground text-lg">
                        Describe your tasks in natural language and let AI create your perfect schedule
                    </p>
                </div>

                {/* Info Banner */}
                <Card className="mb-6 border-accent/30 bg-accent/5">
                    <CardContent className="flex items-start gap-4 py-4">
                        <Lightbulb className="w-6 h-6 text-accent flex-shrink-0 mt-1" />
                        <div>
                            <p className="font-medium text-foreground">How it works</p>
                            <p className="text-sm text-muted-foreground mt-1">
                                Simply describe what you need to accomplish today. Write naturally, like "I need to finish my math homework,
                                then study for biology test, grab lunch, work on the group project presentation, and review notes for tomorrow's quiz."
                                We'll parse your text and create an optimized schedule automatically!
                            </p>
                        </div>
                    </CardContent>
                </Card>

                <div className="grid lg:grid-cols-2 gap-6">
                    {/* Task Description Input Section */}
                    <Card className="border-border/50">
                        <CardHeader>
                            <CardTitle className="flex items-center gap-2">
                                <FileText className="w-5 h-5 text-accent" />
                                Describe Your Tasks
                            </CardTitle>
                            <CardDescription>
                                Write about what you need to accomplish today in your own words
                            </CardDescription>
                        </CardHeader>
                        <CardContent className="space-y-4">
                            <div className="relative">
                                <Textarea
                                    placeholder="Example: Today I need to complete my physics assignment which might take about an hour. Then I should review the lecture notes from yesterday's class. After lunch, I have to work on the research paper introduction and prepare slides for tomorrow's presentation. I also need to send an email to my professor about the project deadline..."
                                    value={taskDescription}
                                    onChange={(e) => setTaskDescription(e.target.value)}
                                    className="min-h-[280px] resize-none text-base leading-relaxed"
                                />
                                <div className="absolute bottom-3 right-3 text-xs text-muted-foreground">
                                    {taskDescription.length} characters
                                </div>
                            </div>

                            {/* Action Buttons */}
                            <div className="flex gap-3">
                                <Button
                                    onClick={handleGenerateSchedule}
                                    disabled={generating || !taskDescription.trim()}
                                    className="flex-1 bg-accent hover:bg-accent/90"
                                    size="lg"
                                >
                                    {generating ? (
                                        <>
                                            <Brain className="w-5 h-5 mr-2 animate-pulse" />
                                            Generating schedule...
                                        </>
                                    ) : (
                                        <>
                                            <Wand2 className="w-5 h-5 mr-2" />
                                            Generate Schedule
                                        </>
                                    )}
                                </Button>
                                {(taskDescription || schedule.length > 0) && (
                                    <Button
                                        variant="outline"
                                        onClick={clearAll}
                                        size="lg"
                                    >
                                        Clear
                                    </Button>
                                )}
                            </div>

                            {/* Quick Examples */}
                            <div className="pt-4 border-t border-border/50">
                                <p className="text-sm font-medium text-muted-foreground mb-3">Quick templates:</p>
                                <div className="flex flex-wrap gap-2">
                                    {[
                                        "Study session with breaks",
                                        "Work day planning",
                                        "Assignment deadline prep",
                                    ].map((template) => (
                                        <Button
                                            key={template}
                                            variant="outline"
                                            size="sm"
                                            className="text-xs"
                                            onClick={() => {
                                                const templates = {
                                                    "Study session with breaks": "Start with reviewing lecture notes for 30 minutes. Then practice problem solving for the upcoming exam. Take a short break. Complete the reading assignment for next class. Finally, summarize key concepts in my notes.",
                                                    "Work day planning": "Check and respond to important emails. Work on the main project deliverable. Have a team meeting. Review and update project documentation. Plan tasks for tomorrow.",
                                                    "Assignment deadline prep": "Outline the main points of the essay. Write the introduction and first body paragraph. Research additional sources. Complete the remaining sections. Proofread and format the final document.",
                                                }
                                                setTaskDescription(templates[template])
                                            }}
                                        >
                                            {template}
                                        </Button>
                                    ))}
                                </div>
                            </div>
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
                            {error ? (
                                <div className="text-center py-12">
                                    <AlertCircle className="w-16 h-16 mx-auto mb-3 text-destructive/50" />
                                    <p className="text-lg mb-1 text-destructive">{error}</p>
                                    <p className="text-sm text-muted-foreground">Try describing your tasks more clearly</p>
                                </div>
                            ) : schedule.length === 0 ? (
                                <div className="text-center py-12 text-muted-foreground">
                                    <Sparkles className="w-16 h-16 mx-auto mb-3 opacity-30" />
                                    <p className="text-lg mb-1">Schedule not generated yet</p>
                                    <p className="text-sm">Describe your tasks and hit the generate button</p>
                                </div>
                            ) : (
                                <div className="space-y-4">
                                    {scheduleInfo && (
                                        <div className="text-sm text-muted-foreground mb-4 p-3 bg-muted/30 rounded-lg">
                                            Found <strong className="text-foreground">{scheduleInfo.tasksFound}</strong> tasks in your description
                                            {scheduleInfo.schedulingWindow && (
                                                <span> • Window: {scheduleInfo.schedulingWindow.start} - {scheduleInfo.schedulingWindow.end}</span>
                                            )}
                                        </div>
                                    )}

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
                                                <div className="flex items-center gap-2">
                                                    {item.priority && (
                                                        <span className={`text-xs px-2 py-0.5 rounded ${item.priority === 'high' ? 'bg-red-500/20 text-red-400' :
                                                                item.priority === 'low' ? 'bg-green-500/20 text-green-400' :
                                                                    'bg-yellow-500/20 text-yellow-400'
                                                            }`}>
                                                            {item.priority}
                                                        </span>
                                                    )}
                                                    <div className="text-xs font-medium text-accent bg-accent/20 px-2 py-1 rounded">
                                                        {item.duration}m
                                                    </div>
                                                </div>
                                            </div>
                                            {item.aiTip && (
                                                <div className="mt-3 p-2 rounded bg-muted/50 border border-border/30">
                                                    <p className="text-xs text-muted-foreground flex items-start gap-2">
                                                        <Sparkles className="w-3 h-3 text-accent mt-0.5 flex-shrink-0" />
                                                        <span>
                                                            <strong>AI Tip:</strong> {item.aiTip}
                                                        </span>
                                                    </p>
                                                </div>
                                            )}
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
            </main>
        </div>
    )
}
