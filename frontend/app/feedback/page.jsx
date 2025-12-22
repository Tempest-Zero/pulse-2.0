"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Navigation } from "@/components/navigation"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { submitFeedback, getUserFeedback } from "@/lib/api/feedback"
import { useAuth } from "@/lib/auth-context"
import {
    Star,
    Send,
    MessageSquare,
    Sparkles,
    Bug,
    Lightbulb,
    Heart,
    CheckCircle2,
    Clock
} from "lucide-react"

export default function FeedbackPage() {
    const { toast } = useToast()
    const { user } = useAuth()
    const [rating, setRating] = useState(0)
    const [hoveredRating, setHoveredRating] = useState(0)
    const [category, setCategory] = useState("general")
    const [review, setReview] = useState("")
    const [submitting, setSubmitting] = useState(false)
    const [submitted, setSubmitted] = useState(false)
    const [feedbackHistory, setFeedbackHistory] = useState([])
    const [loadingHistory, setLoadingHistory] = useState(true)

    const categories = [
        { id: "general", label: "General", icon: MessageSquare, color: "text-accent" },
        { id: "feature", label: "Feature Request", icon: Sparkles, color: "text-chart-2" },
        { id: "bug", label: "Bug Report", icon: Bug, color: "text-destructive" },
        { id: "improvement", label: "Improvement", icon: Lightbulb, color: "text-chart-3" },
    ]

    const ratingLabels = [
        "",
        "Poor - Not satisfied",
        "Fair - Needs improvement",
        "Good - Meets expectations",
        "Great - Exceeds expectations",
        "Excellent - Love it!"
    ]

    useEffect(() => {
        loadFeedbackHistory()
    }, [])

    const loadFeedbackHistory = async () => {
        try {
            setLoadingHistory(true)
            const history = await getUserFeedback(5)
            setFeedbackHistory(history)
        } catch (error) {
            // User might not have feedback yet
            setFeedbackHistory([])
        } finally {
            setLoadingHistory(false)
        }
    }

    const handleSubmit = async () => {
        if (rating === 0) {
            toast({
                title: "Please select a rating",
                description: "Choose how many stars you'd give us",
                variant: "destructive",
            })
            return
        }

        setSubmitting(true)
        try {
            await submitFeedback({
                rating,
                category,
                review: review.trim() || null,
            })

            setSubmitted(true)
            toast({
                title: "Thank you for your feedback! 🎉",
                description: "Your feedback helps us improve Pulse for everyone.",
            })

            // Reset form after short delay
            setTimeout(() => {
                setRating(0)
                setCategory("general")
                setReview("")
                setSubmitted(false)
                loadFeedbackHistory()
            }, 3000)

        } catch (error) {
            toast({
                title: "Error submitting feedback",
                description: error.message,
                variant: "destructive",
            })
        } finally {
            setSubmitting(false)
        }
    }

    const formatDate = (dateString) => {
        const date = new Date(dateString)
        return date.toLocaleDateString('en-US', {
            month: 'short',
            day: 'numeric',
            year: 'numeric'
        })
    }

    return (
        <div className="min-h-screen bg-background">
            <Navigation />

            <div className="container mx-auto px-4 py-8 max-w-4xl">
                <div className="mb-8">
                    <h1 className="text-4xl font-bold mb-2">Share Your Feedback</h1>
                    <p className="text-muted-foreground text-lg">
                        Help us make Pulse even better! Your feedback is incredibly valuable.
                    </p>
                </div>

                {/* Success State */}
                {submitted ? (
                    <Card className="p-12 text-center bg-gradient-to-br from-accent/10 to-chart-2/10 border-accent/30">
                        <div className="w-20 h-20 rounded-full bg-accent/20 flex items-center justify-center mx-auto mb-6">
                            <Heart className="w-10 h-10 text-accent animate-pulse" />
                        </div>
                        <h2 className="text-3xl font-bold mb-4">Thank You! 💜</h2>
                        <p className="text-lg text-muted-foreground">
                            Your feedback has been submitted successfully. We truly appreciate you taking the time to help us improve!
                        </p>
                    </Card>
                ) : (
                    <>
                        {/* Rating Section */}
                        <Card className="p-8 mb-6 bg-gradient-to-br from-primary/5 to-accent/5">
                            <h2 className="text-xl font-bold mb-6 flex items-center gap-2">
                                <Star className="w-5 h-5 text-accent" />
                                How would you rate your experience?
                            </h2>

                            <div className="flex flex-col items-center">
                                <div className="flex gap-3 mb-4">
                                    {[1, 2, 3, 4, 5].map((star) => (
                                        <button
                                            key={star}
                                            onClick={() => setRating(star)}
                                            onMouseEnter={() => setHoveredRating(star)}
                                            onMouseLeave={() => setHoveredRating(0)}
                                            className="transition-all duration-200 hover:scale-110"
                                        >
                                            <Star
                                                className={`w-12 h-12 transition-colors ${star <= (hoveredRating || rating)
                                                        ? "text-yellow-400 fill-yellow-400"
                                                        : "text-muted-foreground/30"
                                                    }`}
                                            />
                                        </button>
                                    ))}
                                </div>
                                <p className="text-sm text-muted-foreground h-6">
                                    {rating > 0 ? ratingLabels[rating] : "Click to rate"}
                                </p>
                            </div>
                        </Card>

                        {/* Category Selection */}
                        <Card className="p-6 mb-6">
                            <h2 className="text-xl font-bold mb-4">What's this about?</h2>
                            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                                {categories.map((cat) => {
                                    const Icon = cat.icon
                                    const isSelected = category === cat.id
                                    return (
                                        <button
                                            key={cat.id}
                                            onClick={() => setCategory(cat.id)}
                                            className={`flex flex-col items-center gap-2 p-4 rounded-xl border-2 transition-all ${isSelected
                                                    ? "border-accent bg-accent/10 scale-105"
                                                    : "border-border/50 hover:border-accent/50 hover:bg-muted/50"
                                                }`}
                                        >
                                            <Icon className={`w-6 h-6 ${isSelected ? cat.color : "text-muted-foreground"}`} />
                                            <span className={`text-sm font-medium ${isSelected ? "" : "text-muted-foreground"}`}>
                                                {cat.label}
                                            </span>
                                        </button>
                                    )
                                })}
                            </div>
                        </Card>

                        {/* Review Text */}
                        <Card className="p-6 mb-6">
                            <h2 className="text-xl font-bold mb-4">Tell us more (optional)</h2>
                            <Textarea
                                placeholder="Share your thoughts, suggestions, or report any issues you've encountered..."
                                value={review}
                                onChange={(e) => setReview(e.target.value)}
                                className="min-h-32 resize-none"
                                maxLength={2000}
                            />
                            <p className="text-xs text-muted-foreground mt-2 text-right">
                                {review.length}/2000 characters
                            </p>
                        </Card>

                        {/* Submit Button */}
                        <Button
                            onClick={handleSubmit}
                            disabled={submitting || rating === 0}
                            className="w-full py-6 text-lg bg-accent text-accent-foreground hover:bg-accent/90 rounded-xl"
                        >
                            {submitting ? (
                                <>
                                    <div className="w-5 h-5 border-2 border-accent-foreground/30 border-t-accent-foreground rounded-full animate-spin mr-2" />
                                    Submitting...
                                </>
                            ) : (
                                <>
                                    <Send className="w-5 h-5 mr-2" />
                                    Submit Feedback
                                </>
                            )}
                        </Button>
                    </>
                )}

                {/* Previous Feedback */}
                {feedbackHistory.length > 0 && !submitted && (
                    <Card className="p-6 mt-8">
                        <h2 className="text-xl font-bold mb-4 flex items-center gap-2">
                            <Clock className="w-5 h-5 text-muted-foreground" />
                            Your Previous Feedback
                        </h2>
                        <div className="space-y-4">
                            {feedbackHistory.map((feedback) => (
                                <div
                                    key={feedback.id}
                                    className="p-4 rounded-xl bg-muted/30 border border-border/50"
                                >
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-2">
                                            <div className="flex">
                                                {[1, 2, 3, 4, 5].map((star) => (
                                                    <Star
                                                        key={star}
                                                        className={`w-4 h-4 ${star <= feedback.rating
                                                                ? "text-yellow-400 fill-yellow-400"
                                                                : "text-muted-foreground/30"
                                                            }`}
                                                    />
                                                ))}
                                            </div>
                                            <span className="text-sm text-muted-foreground capitalize">
                                                {feedback.category}
                                            </span>
                                        </div>
                                        <span className="text-xs text-muted-foreground">
                                            {formatDate(feedback.createdAt)}
                                        </span>
                                    </div>
                                    {feedback.review && (
                                        <p className="text-sm text-muted-foreground line-clamp-2">
                                            {feedback.review}
                                        </p>
                                    )}
                                </div>
                            ))}
                        </div>
                    </Card>
                )}

                {/* Appreciation Note */}
                <div className="mt-8 text-center text-muted-foreground">
                    <p className="text-sm">
                        🙏 Every piece of feedback helps us build a better product. Thank you for being part of the Pulse community!
                    </p>
                </div>
            </div>
        </div>
    )
}
