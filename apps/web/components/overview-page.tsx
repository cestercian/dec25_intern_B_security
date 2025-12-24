"use client"

import { useEffect, useState } from "react"
import { useSession } from "next-auth/react"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Shield, AlertTriangle, Mail, TrendingUp, TrendingDown, CheckCircle } from "lucide-react"
import { Badge } from "@/components/ui/badge"
import { ChartAreaInteractive } from "@/components/chart-area-interactive"
import { fetchEmails, type Email } from "@/lib/api"

export function OverviewPage() {
  const { data: session } = useSession()
  const [emails, setEmails] = useState<Email[]>([])
  const [loading, setLoading] = useState(true)

  useEffect(() => {
    const loadEmails = async () => {
      if (!session?.idToken) return
      try {
        const data = await fetchEmails(session.idToken)
        setEmails(data)
      } catch (error) {
        console.error("Failed to fetch emails:", error)
      } finally {
        setLoading(false)
      }
    }
    loadEmails()
  }, [session])

  // Calculate stats from emails
  const totalEmails = emails.length
  const safeEmails = emails.filter(e => e.risk_tier === "SAFE").length
  const cautiousEmails = emails.filter(e => e.risk_tier === "CAUTIOUS").length
  const threatEmails = emails.filter(e => e.risk_tier === "THREAT").length
  const analyzedEmails = safeEmails + cautiousEmails + threatEmails
  const protectionRate = analyzedEmails > 0 
    ? ((safeEmails / analyzedEmails) * 100).toFixed(1)
    : "100.0"

  // Recent emails for display
  const recentEmails = emails.slice(0, 5).map(email => ({
    id: email.id,
    recipient: email.recipient,
    subject: email.subject,
    status: email.risk_tier === "THREAT" ? "blocked" : email.risk_tier === "SAFE" ? "clean" : "review",
    threat: email.risk_tier === "THREAT" ? "Potential Threat" : null,
  }))

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-3xl font-bold text-foreground">Overview</h1>
        <p className="text-muted-foreground">Your email security dashboard</p>
      </div>

      {/* Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <Card className="border-border">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Emails Scanned</CardTitle>
            <Mail className="h-4 w-4 text-muted-foreground" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {loading ? "..." : totalEmails}
            </div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <TrendingUp className="h-3 w-3 text-green-500" />
              All time total
            </p>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Safe Emails</CardTitle>
            <CheckCircle className="h-4 w-4 text-green-500" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-green-500">
              {loading ? "..." : safeEmails}
            </div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              Verified as safe
            </p>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Threats Detected</CardTitle>
            <AlertTriangle className="h-4 w-4 text-destructive" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">
              {loading ? "..." : threatEmails}
            </div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <TrendingDown className="h-3 w-3 text-green-500" />
              Blocked automatically
            </p>
          </CardContent>
        </Card>

        <Card className="border-border">
          <CardHeader className="flex flex-row items-center justify-between pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">Protection Rate</CardTitle>
            <Shield className="h-4 w-4 text-primary" />
          </CardHeader>
          <CardContent>
            <div className="text-2xl font-bold text-foreground">{protectionRate}%</div>
            <p className="text-xs text-muted-foreground flex items-center gap-1 mt-1">
              <span className="text-primary">Excellent</span> security
            </p>
          </CardContent>
        </Card>
      </div>

      {/* Email Activity Chart */}
      <ChartAreaInteractive />

      {/* Recent Email Activity */}
      <Card className="border-border">
        <CardHeader>
          <CardTitle className="text-foreground">Recent Email Activity</CardTitle>
          <CardDescription>Latest emails analyzed by MailShieldAI</CardDescription>
        </CardHeader>
        <CardContent>
          {loading ? (
            <p className="text-sm text-muted-foreground">Loading emails...</p>
          ) : recentEmails.length === 0 ? (
            <p className="text-sm text-muted-foreground">No emails scanned yet. Sync your Gmail to get started.</p>
          ) : (
            <div className="space-y-3">
              {recentEmails.map((email) => (
                <div
                  key={email.id}
                  className="flex items-center justify-between p-3 rounded-lg border border-border hover:bg-accent/50 transition-colors"
                >
                  <div className="flex items-center gap-4 flex-1">
                    <div
                      className={`w-2 h-2 rounded-full ${
                        email.status === "blocked" ? "bg-destructive" : 
                        email.status === "review" ? "bg-yellow-500" : "bg-green-500"
                      }`}
                    />
                    <div className="flex-1 min-w-0">
                      <p className="text-sm font-medium text-foreground truncate">{email.subject}</p>
                      <p className="text-xs text-muted-foreground">{email.recipient}</p>
                    </div>
                  </div>
                  <div className="flex items-center gap-2">
                    {email.status === "blocked" && email.threat && (
                      <Badge variant="destructive" className="text-xs">
                        {email.threat}
                      </Badge>
                    )}
                    <Badge 
                      variant={email.status === "blocked" ? "outline" : email.status === "review" ? "secondary" : "secondary"} 
                      className="text-xs"
                    >
                      {email.status === "blocked" ? "Blocked" : email.status === "review" ? "Review" : "Safe"}
                    </Badge>
                  </div>
                </div>
              ))}
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  )
}
