"use client"

import { useState, useEffect } from "react"
import { Card } from "@/components/ui/card"
import { Button } from "@/components/ui/button"
import { Navigation } from "@/components/navigation"
import { Textarea } from "@/components/ui/textarea"
import { useToast } from "@/hooks/use-toast"
import { submitFeedback, getAllFeedback, getFeedbackStats } from "@/lib/api/feedback"
import { useAuth } from "@/lib/auth-context"
import Link from "next/link"
import {
    Star,
    Send,
    MessageSquare,
    Sparkles,
    Bug,
    Lightbulb,
    Heart,
    Users,
    TrendingUp,
    LogIn
} from "lucide-react"

export default function FeedbackPage() {
    const { toast } = useToast()
    const { user, isAuthenticated } = useAuth()
    const [rating, setRating] = useState(0)
    const [hoveredRating, setHoveredRating] = useState(0)
    const [category, setCategory] = useState("general")
    const [review, setReview] = useState("")
    const [submitting, setSubmitting] = useState(false)
    const [submitted, setSubmitted] = useState(false)
    const [allFeedback, setAllFeedback] = useState([])
    const [stats, setStats] = useState(null)
    const [loading, setLoading] = useState(true)

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
        loadPublicFeedback()
    }, [])

    const loadPublicFeedback = async () => {
        try {
            setLoading(true)
            const [feedbackData, statsData] = await Promise.all([
                getAllFeedback(50),
                getFeedbackStats()
            ])
            setAllFeedback(feedbackData)
            setStats(statsData)
        } catch (error) {
            console.error('Error loading feedback:', error)
            setAllFeedback([])
        } finally {
            setLoading(false)
        }
    }

    const handleSubmit = async () => {
        if (!isAuthenticated) {
            toast({
                title: "Please sign in",
                description: "You need to be logged in to submit feedback",
                variant: "destructive",
            })
            return
        }

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

            // Reset form and reload feedback after short delay
            setTimeout(() => {
                setRating(0)
                setCategory("general")
                setReview("")
                setSubmitted(false)
                loadPublicFeedback()
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

    const getCategoryIcon = (categoryId) => {
        const cat = categories.find(c => c.id === categoryId)
        return cat ? cat.icon : MessageSquare
    }

    const getCategoryColor = (categoryId) => {
        const cat = categories.find(c => c.id === categoryId)
        return cat ? cat.color : "text-muted-foreground"
    }

    return (
        <div className="min-h-screen bg-background">
            <Navigation />

            <div className="container mx-auto px-4 py-8 max-w-6xl">
                <div className="mb-8 text-center">
                    <h1 className="text-4xl font-bold mb-2">Community Feedback</h1>
                    <p className="text-muted-foreground text-lg">
                        See what others are saying about Pulse and share your experience!
                    </p>
                </div>

                {/* Stats Overview */}
                {stats && (
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
                        <Card className="p-4 text-center">
                            <Users className="w-8 h-8 mx-auto mb-2 text-accent" />
                            <div className="text-2xl font-bold">{stats.totalFeedback}</div>
                            <div className="text-sm text-muted-foreground">Total Reviews</div>
                        </Card>
                        <Card className="p-4 text-center">
                            <Star className="w-8 h-8 mx-auto mb-2 text-yellow-400" />
                            <div className="text-2xl font-bold">{stats.averageRating.toFixed(1)}</div>
                            <div className="text-sm text-muted-foreground">Average Rating</div>
                        </Card>
                        <Card className="p-4 text-center">
                            <TrendingUp className="w-8 h-8 mx-auto mb-2 text-chart-2" />
                            <div className="text-2xl font-bold">{stats.ratingDistribution['5'] || 0}</div>
                            <div className="text-sm text-muted-foreground">5-Star Reviews</div>
                        </Card>
                        <Card className="p-4 text-center">
                            <Heart className="w-8 h-8 mx-auto mb-2 text-chart-4" />
                            <div className="text-2xl font-bold">
                                {stats.totalFeedback > 0
                                    ? Math.round(((stats.ratingDistribution['4'] || 0) + (stats.ratingDistribution['5'] || 0)) / stats.totalFeedback * 100)
                                    : 0}%
                            </div>
                            <div className="text-sm text-muted-foreground">Satisfaction</div>
                        </Card>
                    </div>
                )}

                <div className="grid lg:grid-cols-2 gap-8">
                    {/* Left Column - Submit Feedback */}
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold flex items-center gap-2">
                            <MessageSquare className="w-6 h-6 text-accent" />
                            Share Your Feedback
                        </h2>

                        {!isAuthenticated ? (
                            // Not logged in - show login prompt
                            <Card className="p-8 text-center bg-gradient-to-br from-primary/5 to-accent/5">
                                <LogIn className="w-12 h-12 mx-auto mb-4 text-accent" />
                                <h3 className="text-xl font-bold mb-2">Sign in to Leave Feedback</h3>
                                <p className="text-muted-foreground mb-6">
                                    Join our community and share your experience with Pulse!
                                </p>
                                <Button asChild className="bg-accent text-accent-foreground hover:bg-accent/90">
                                    <Link href="/auth">Sign In to Submit Feedback</Link>
                                </Button>
                            </Card>
                        ) : submitted ? (
                            // Success state
                            <Card className="p-8 text-center bg-gradient-to-br from-accent/10 to-chart-2/10 border-accent/30">
                                <div className="w-16 h-16 rounded-full bg-accent/20 flex items-center justify-center mx-auto mb-4">
                                    <Heart className="w-8 h-8 text-accent animate-pulse" />
                                </div>
                                <h3 className="text-2xl font-bold mb-2">Thank You! 💜</h3>
                                <p className="text-muted-foreground">
                                    Your feedback has been submitted successfully!
                                </p>
                            </Card>
                        ) : (
                            // Feedback form
                            <>
                                {/* Rating Section */}
                                <Card className="p-6 bg-gradient-to-br from-primary/5 to-accent/5">
                                    <h3 className="text-lg font-semibold mb-4">How would you rate Pulse?</h3>
                                    <div className="flex flex-col items-center">
                                        <div className="flex gap-2 mb-3">
                                            {[1, 2, 3, 4, 5].map((star) => (
                                                <button
                                                    key={star}
                                                    onClick={() => setRating(star)}
                                                    onMouseEnter={() => setHoveredRating(star)}
                                                    onMouseLeave={() => setHoveredRating(0)}
                                                    className="transition-all duration-200 hover:scale-110"
                                                >
                                                    <Star
                                                        className={`w-10 h-10 transition-colors ${star <= (hoveredRating || rating)
                                                                ? "text-yellow-400 fill-yellow-400"
                                                                : "text-muted-foreground/30"
                                                            }`}
                                                    />
                                                </button>
                                            ))}
                                        </div>
                                        <p className="text-sm text-muted-foreground h-5">
                                            {rating > 0 ? ratingLabels[rating] : "Click to rate"}
                                        </p>
                                    </div>
                                </Card>

                                {/* Category Selection */}
                                <Card className="p-6">
                                    <h3 className="text-lg font-semibold mb-4">What's this about?</h3>
                                    <div className="grid grid-cols-2 gap-3">
                                        {categories.map((cat) => {
                                            const Icon = cat.icon
                                            const isSelected = category === cat.id
                                            return (
                                                <button
                                                    key={cat.id}
                                                    onClick={() => setCategory(cat.id)}
                                                    className={`flex items-center gap-2 p-3 rounded-xl border-2 transition-all ${isSelected
                                                            ? "border-accent bg-accent/10"
                                                            : "border-border/50 hover:border-accent/50"
                                                        }`}
                                                >
                                                    <Icon className={`w-5 h-5 ${isSelected ? cat.color : "text-muted-foreground"}`} />
                                                    <span className={`text-sm font-medium ${isSelected ? "" : "text-muted-foreground"}`}>
                                                        {cat.label}
                                                    </span>
                                                </button>
                                            )
                                        })}
                                    </div>
                                </Card>

                                {/* Review Text */}
                                <Card className="p-6">
                                    <h3 className="text-lg font-semibold mb-4">Tell us more (optional)</h3>
                                    <Textarea
                                        placeholder="Share your thoughts, suggestions, or feedback..."
                                        value={review}
                                        onChange={(e) => setReview(e.target.value)}
                                        className="min-h-24 resize-none"
                                        maxLength={2000}
                                    />
                                    <p className="text-xs text-muted-foreground mt-2 text-right">
                                        {review.length}/2000
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
                    </div>

                    {/* Right Column - All Reviews */}
                    <div className="space-y-6">
                        <h2 className="text-2xl font-bold flex items-center gap-2">
                            <Users className="w-6 h-6 text-chart-2" />
                            Community Reviews
                        </h2>

                        {loading ? (
                            <Card className="p-8 text-center">
                                <div className="w-8 h-8 border-2 border-accent/30 border-t-accent rounded-full animate-spin mx-auto mb-4" />
                                <p className="text-muted-foreground">Loading reviews...</p>
                            </Card>
                        ) : allFeedback.length === 0 ? (
                            <Card className="p-8 text-center bg-muted/30">
                                <MessageSquare className="w-12 h-12 mx-auto mb-4 text-muted-foreground/50" />
                                <h3 className="text-lg font-semibold mb-2">No reviews yet</h3>
                                <p className="text-muted-foreground">
                                    Be the first to share your experience!
                                </p>
                            </Card>
                        ) : (
                            <div className="space-y-4 max-h-[600px] overflow-y-auto pr-2">
                                {allFeedback.map((feedback) => {
                                    const CategoryIcon = getCategoryIcon(feedback.category)
                                    return (
                                        <Card key={feedback.id} className="p-5">
                                            <div className="flex items-start justify-between mb-3">
                                                <div className="flex items-center gap-3">
                                                    <div className="w-10 h-10 rounded-full bg-accent/20 flex items-center justify-center text-lg">
                                                        {feedback.username ? feedback.username.charAt(0).toUpperCase() : '?'}
                                                    </div>
                                                    <div>
                                                        <div className="font-semibold">{feedback.username || 'Anonymous'}</div>
                                                        <div className="flex items-center gap-2 text-xs text-muted-foreground">
                                                            <span>{formatDate(feedback.createdAt)}</span>
                                                            <span>•</span>
                                                            <span className={`flex items-center gap-1 ${getCategoryColor(feedback.category)}`}>
                                                                <CategoryIcon className="w-3 h-3" />
                                                                {feedback.category}
                                                            </span>
                                                        </div>
                                                    </div>
                                                </div>
                                                <div className="flex">
                                                    {[1, 2, 3, 4, 5].map((star) => (
                                                        <Star
                                                            key={star}
                                                            className={`w-4 h-4 ${star <= feedback.rating
                                                                    ? "text-yellow-400 fill-yellow-400"
                                                                    : "text-muted-foreground/20"
                                                                }`}
                                                        />
                                                    ))}
                                                </div>
                                            </div>
                                            {feedback.review && (
                                                <p className="text-sm text-muted-foreground leading-relaxed">
                                                    "{feedback.review}"
                                                </p>
                                            )}
                                        </Card>
                                    )
                                })}
                            </div>
                        )}
                    </div>
                </div>

                {/* Footer Note */}
                <div className="mt-12 text-center text-muted-foreground">
                    <p className="text-sm">
                        🙏 Every piece of feedback helps us build a better product. Thank you for being part of the Pulse community!
                    </p>
                </div>
            </div>
        </div>
    )
}
