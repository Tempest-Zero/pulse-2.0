"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Badge } from "@/components/ui/badge"
import { getRecommendation, submitFeedback, getPhase } from "@/lib/api/ai"
import { useToast } from "@/hooks/use-toast"
import { Sparkles, CheckCircle2, XCircle, Minus, RefreshCw, Loader2, Target, Zap, Coffee, Brain, Calendar } from "lucide-react"

export function AIRecommendation({ onTaskSelect, onStartFocus }) {
  const { toast } = useToast()
  const [recommendation, setRecommendation] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)
  const [phase, setPhase] = useState(null)
  const [submittingFeedback, setSubmittingFeedback] = useState(false)

  const loadRecommendation = async () => {
    try {
      setLoading(true)
      setError(null)
      const rec = await getRecommendation()
      setRecommendation(rec)
    } catch (err) {
      console.error('Failed to load recommendation:', err)
      setError(err.message)
      toast({
        title: "Error loading recommendation",
        description: err.message,
        variant: "destructive",
      })
    } finally {
      setLoading(false)
    }
  }

  const loadPhase = async () => {
    try {
      const phaseData = await getPhase()
      setPhase(phaseData)
    } catch (err) {
      console.error('Failed to load phase:', err)
    }
  }

  useEffect(() => {
    loadRecommendation()
    loadPhase()
  }, [])

  const handleAccept = () => {
    if (recommendation?.suggested_task) {
      if (onStartFocus) {
        onStartFocus({
          id: recommendation.suggested_task.id,
          title: recommendation.suggested_task.title,
          duration: recommendation.suggested_duration_minutes / 60,
        })
      } else if (onTaskSelect) {
        onTaskSelect(recommendation.suggested_task)
      }
    }
  }

  const handleFeedback = async (outcome, rating = null) => {
    if (!recommendation) return

    try {
      setSubmittingFeedback(true)
      await submitFeedback({
        recommendation_id: recommendation.recommendation_id,
        outcome,
        rating,
      })
      
      toast({
        title: "Feedback submitted",
        description: "Thanks for helping the AI learn!",
      })
      
      // Reload recommendation after feedback
      await loadRecommendation()
    } catch (err) {
      console.error('Failed to submit feedback:', err)
      toast({
        title: "Error submitting feedback",
        description: err.message,
        variant: "destructive",
      })
    } finally {
      setSubmittingFeedback(false)
    }
  }

  const getActionIcon = (actionType) => {
    switch (actionType) {
      case 'DEEP_FOCUS':
        return <Target className="w-5 h-5" />
      case 'LIGHT_TASK':
        return <Zap className="w-5 h-5" />
      case 'BREAK':
        return <Coffee className="w-5 h-5" />
      case 'REFLECTION':
        return <Brain className="w-5 h-5" />
      case 'PLANNING':
        return <Calendar className="w-5 h-5" />
      default:
        return <Sparkles className="w-5 h-5" />
    }
  }

  const getPhaseColor = (phase) => {
    switch (phase) {
      case 'bootstrap':
        return 'bg-blue-500/20 text-blue-500 border-blue-500/30'
      case 'transition':
        return 'bg-yellow-500/20 text-yellow-500 border-yellow-500/30'
      case 'learned':
        return 'bg-green-500/20 text-green-500 border-green-500/30'
      default:
        return 'bg-muted text-muted-foreground border-border'
    }
  }

  if (loading && !recommendation) {
    return (
      <Card className="p-6 bg-gradient-to-br from-accent/10 to-primary/10 border-accent/30">
        <div className="flex items-center justify-center gap-3 text-muted-foreground">
          <Loader2 className="w-5 h-5 animate-spin" />
          <span>Loading AI recommendation...</span>
        </div>
      </Card>
    )
  }

  if (error && !recommendation) {
    return (
      <Card className="p-6 bg-destructive/10 border-destructive/30">
        <div className="text-center">
          <p className="text-destructive mb-4">Failed to load recommendation</p>
          <Button onClick={loadRecommendation} variant="outline" size="sm">
            <RefreshCw className="w-4 h-4 mr-2" />
            Retry
          </Button>
        </div>
      </Card>
    )
  }

  if (!recommendation) return null

  return (
    <Card className="p-6 bg-gradient-to-br from-accent/10 to-primary/10 border-accent/30">
      <div className="flex items-start justify-between mb-4">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center">
            {getActionIcon(recommendation.action_type)}
          </div>
          <div>
            <h3 className="font-bold text-lg flex items-center gap-2">
              AI Recommendation
            </h3>
            {phase && (
              <Badge variant="outline" className={`mt-1 ${getPhaseColor(phase.phase)}`}>
                {phase.phase}
              </Badge>
            )}
          </div>
        </div>
        <Button
          variant="ghost"
          size="sm"
          onClick={loadRecommendation}
          disabled={loading}
        >
          <RefreshCw className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
        </Button>
      </div>

      <div className="space-y-4">
        <div>
          <div className="text-xl font-bold mb-2">
            {recommendation.action_display_name}
          </div>
          <p className="text-muted-foreground leading-relaxed">
            {recommendation.explanation}
          </p>
        </div>

        {recommendation.suggested_task && (
          <div className="p-4 rounded-lg bg-background/50 border border-border/50">
            <div className="flex items-start justify-between mb-2">
              <div className="flex items-center gap-2">
                <Target className="w-4 h-4 text-accent" />
                <span className="font-medium">{recommendation.suggested_task.title}</span>
              </div>
            </div>
            <div className="flex items-center gap-4 text-sm text-muted-foreground">
              <span>{recommendation.suggested_duration_minutes} min</span>
              {recommendation.suggested_task.priority && (
                <Badge variant="secondary">
                  Priority: {recommendation.suggested_task.priority}
                </Badge>
              )}
            </div>
          </div>
        )}

        {recommendation.alternative_tasks && recommendation.alternative_tasks.length > 0 && (
          <div className="p-4 rounded-lg bg-muted/30 border border-border/50">
            <div className="text-sm font-medium mb-2 text-muted-foreground">Alternatives:</div>
            <div className="space-y-2">
              {recommendation.alternative_tasks.map((task) => (
                <div key={task.id} className="text-sm flex items-center justify-between">
                  <span>{task.title}</span>
                  <span className="text-muted-foreground">{task.estimated_duration_minutes} min</span>
                </div>
              ))}
            </div>
          </div>
        )}

        <div className="flex items-center gap-4 text-xs text-muted-foreground">
          <span>Confidence: {Math.round(recommendation.confidence * 100)}%</span>
          <span>•</span>
          <span className="capitalize">Strategy: {recommendation.strategy}</span>
        </div>

        <div className="flex items-center gap-2 pt-2 border-t border-border/50">
          {recommendation.suggested_task && (
            <Button
              onClick={handleAccept}
              className="flex-1 bg-accent text-accent-foreground hover:bg-accent/90"
              disabled={submittingFeedback}
            >
              Start Task
            </Button>
          )}
          
          <div className="flex gap-1">
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleFeedback('completed', 5)}
              disabled={submittingFeedback}
              title="Completed"
            >
              <CheckCircle2 className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleFeedback('partial', 3)}
              disabled={submittingFeedback}
              title="Partial"
            >
              <Minus className="w-4 h-4" />
            </Button>
            <Button
              variant="outline"
              size="sm"
              onClick={() => handleFeedback('skipped', 1)}
              disabled={submittingFeedback}
              title="Skipped"
            >
              <XCircle className="w-4 h-4" />
            </Button>
          </div>
        </div>
      </div>
    </Card>
  )
}

