"use client"

import * as React from "react"
import { Area, AreaChart, CartesianGrid, XAxis } from "recharts"

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card"
import {
  ChartContainer,
  ChartLegend,
  ChartLegendContent,
  ChartTooltip,
  ChartTooltipContent,
  type ChartConfig,
} from "@/components/ui/chart"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"

export const description = "Email activity chart showing threats detected and emails scanned"

const chartData = [
  { date: "2024-10-01", threatsDetected: 222, emailsScanned: 150 },
  { date: "2024-10-02", threatsDetected: 97, emailsScanned: 180 },
  { date: "2024-10-03", threatsDetected: 167, emailsScanned: 120 },
  { date: "2024-10-04", threatsDetected: 242, emailsScanned: 260 },
  { date: "2024-10-05", threatsDetected: 373, emailsScanned: 290 },
  { date: "2024-10-06", threatsDetected: 301, emailsScanned: 340 },
  { date: "2024-10-07", threatsDetected: 245, emailsScanned: 180 },
  { date: "2024-10-08", threatsDetected: 409, emailsScanned: 320 },
  { date: "2024-10-09", threatsDetected: 59, emailsScanned: 110 },
  { date: "2024-10-10", threatsDetected: 261, emailsScanned: 190 },
  { date: "2024-10-11", threatsDetected: 327, emailsScanned: 350 },
  { date: "2024-10-12", threatsDetected: 292, emailsScanned: 210 },
  { date: "2024-10-13", threatsDetected: 342, emailsScanned: 380 },
  { date: "2024-10-14", threatsDetected: 137, emailsScanned: 220 },
  { date: "2024-10-15", threatsDetected: 120, emailsScanned: 170 },
  { date: "2024-10-16", threatsDetected: 138, emailsScanned: 190 },
  { date: "2024-10-17", threatsDetected: 446, emailsScanned: 360 },
  { date: "2024-10-18", threatsDetected: 364, emailsScanned: 410 },
  { date: "2024-10-19", threatsDetected: 243, emailsScanned: 180 },
  { date: "2024-10-20", threatsDetected: 89, emailsScanned: 150 },
  { date: "2024-10-21", threatsDetected: 137, emailsScanned: 200 },
  { date: "2024-10-22", threatsDetected: 224, emailsScanned: 170 },
  { date: "2024-10-23", threatsDetected: 138, emailsScanned: 230 },
  { date: "2024-10-24", threatsDetected: 387, emailsScanned: 290 },
  { date: "2024-10-25", threatsDetected: 215, emailsScanned: 250 },
  { date: "2024-10-26", threatsDetected: 75, emailsScanned: 130 },
  { date: "2024-10-27", threatsDetected: 383, emailsScanned: 420 },
  { date: "2024-10-28", threatsDetected: 122, emailsScanned: 180 },
  { date: "2024-10-29", threatsDetected: 315, emailsScanned: 240 },
  { date: "2024-10-30", threatsDetected: 454, emailsScanned: 380 },
  { date: "2024-10-31", threatsDetected: 165, emailsScanned: 220 },
  { date: "2024-11-01", threatsDetected: 293, emailsScanned: 310 },
  { date: "2024-11-02", threatsDetected: 247, emailsScanned: 190 },
  { date: "2024-11-03", threatsDetected: 385, emailsScanned: 420 },
  { date: "2024-11-04", threatsDetected: 481, emailsScanned: 390 },
  { date: "2024-11-05", threatsDetected: 498, emailsScanned: 520 },
  { date: "2024-11-06", threatsDetected: 388, emailsScanned: 300 },
  { date: "2024-11-07", threatsDetected: 149, emailsScanned: 210 },
  { date: "2024-11-08", threatsDetected: 227, emailsScanned: 180 },
  { date: "2024-11-09", threatsDetected: 293, emailsScanned: 330 },
  { date: "2024-11-10", threatsDetected: 335, emailsScanned: 270 },
  { date: "2024-11-11", threatsDetected: 197, emailsScanned: 240 },
  { date: "2024-11-12", threatsDetected: 197, emailsScanned: 160 },
  { date: "2024-11-13", threatsDetected: 448, emailsScanned: 490 },
  { date: "2024-11-14", threatsDetected: 473, emailsScanned: 380 },
  { date: "2024-11-15", threatsDetected: 338, emailsScanned: 400 },
  { date: "2024-11-16", threatsDetected: 499, emailsScanned: 420 },
  { date: "2024-11-17", threatsDetected: 315, emailsScanned: 350 },
  { date: "2024-11-18", threatsDetected: 235, emailsScanned: 180 },
  { date: "2024-11-19", threatsDetected: 177, emailsScanned: 230 },
  { date: "2024-11-20", threatsDetected: 82, emailsScanned: 140 },
  { date: "2024-11-21", threatsDetected: 81, emailsScanned: 120 },
  { date: "2024-11-22", threatsDetected: 252, emailsScanned: 290 },
  { date: "2024-11-23", threatsDetected: 294, emailsScanned: 220 },
  { date: "2024-11-24", threatsDetected: 201, emailsScanned: 250 },
  { date: "2024-11-25", threatsDetected: 213, emailsScanned: 170 },
  { date: "2024-11-26", threatsDetected: 420, emailsScanned: 460 },
  { date: "2024-11-27", threatsDetected: 233, emailsScanned: 190 },
  { date: "2024-11-28", threatsDetected: 78, emailsScanned: 130 },
  { date: "2024-11-29", threatsDetected: 340, emailsScanned: 280 },
  { date: "2024-11-30", threatsDetected: 178, emailsScanned: 230 },
  { date: "2024-12-01", threatsDetected: 178, emailsScanned: 200 },
  { date: "2024-12-02", threatsDetected: 470, emailsScanned: 410 },
  { date: "2024-12-03", threatsDetected: 103, emailsScanned: 160 },
  { date: "2024-12-04", threatsDetected: 439, emailsScanned: 380 },
  { date: "2024-12-05", threatsDetected: 88, emailsScanned: 140 },
  { date: "2024-12-06", threatsDetected: 294, emailsScanned: 250 },
  { date: "2024-12-07", threatsDetected: 323, emailsScanned: 370 },
  { date: "2024-12-08", threatsDetected: 385, emailsScanned: 320 },
  { date: "2024-12-09", threatsDetected: 438, emailsScanned: 480 },
  { date: "2024-12-10", threatsDetected: 155, emailsScanned: 200 },
  { date: "2024-12-11", threatsDetected: 92, emailsScanned: 150 },
  { date: "2024-12-12", threatsDetected: 492, emailsScanned: 420 },
  { date: "2024-12-13", threatsDetected: 81, emailsScanned: 130 },
  { date: "2024-12-14", threatsDetected: 426, emailsScanned: 380 },
  { date: "2024-12-15", threatsDetected: 307, emailsScanned: 350 },
  { date: "2024-12-16", threatsDetected: 371, emailsScanned: 310 },
  { date: "2024-12-17", threatsDetected: 475, emailsScanned: 520 },
  { date: "2024-12-18", threatsDetected: 107, emailsScanned: 170 },
  { date: "2024-12-19", threatsDetected: 341, emailsScanned: 290 },
  { date: "2024-12-20", threatsDetected: 408, emailsScanned: 450 },
  { date: "2024-12-21", threatsDetected: 169, emailsScanned: 210 },
  { date: "2024-12-22", threatsDetected: 317, emailsScanned: 270 },
  { date: "2024-12-23", threatsDetected: 480, emailsScanned: 530 },
  { date: "2024-12-24", threatsDetected: 132, emailsScanned: 180 },
]

const chartConfig = {
  emailActivity: {
    label: "Email Activity",
  },
  threatsDetected: {
    label: "Threats Detected",
    color: "hsl(0 84% 60%)",
  },
  emailsScanned: {
    label: "Emails Scanned",
    color: "hsl(217 91% 60%)",
  },
} satisfies ChartConfig

export function ChartAreaInteractive() {
  const [timeRange, setTimeRange] = React.useState("90d")

  const filteredData = chartData.filter((item) => {
    const date = new Date(item.date)
    const referenceDate = new Date("2024-12-24")
    let daysToSubtract = 90
    if (timeRange === "30d") {
      daysToSubtract = 30
    } else if (timeRange === "7d") {
      daysToSubtract = 7
    }
    const startDate = new Date(referenceDate)
    startDate.setDate(startDate.getDate() - daysToSubtract)
    return date >= startDate
  })

  return (
    <Card className="pt-0 border-border">
      <CardHeader className="flex items-center gap-2 space-y-0 border-b border-border py-5 sm:flex-row">
        <div className="grid flex-1 gap-1">
          <CardTitle className="text-foreground">Email Activity</CardTitle>
          <CardDescription>
            Showing email traffic for the last 3 months
          </CardDescription>
        </div>
        <Select value={timeRange} onValueChange={setTimeRange}>
          <SelectTrigger
            className="hidden w-[160px] rounded-lg sm:ml-auto sm:flex"
            aria-label="Select a value"
          >
            <SelectValue placeholder="Last 3 months" />
          </SelectTrigger>
          <SelectContent className="rounded-xl">
            <SelectItem value="90d" className="rounded-lg">
              Last 3 months
            </SelectItem>
            <SelectItem value="30d" className="rounded-lg">
              Last 30 days
            </SelectItem>
            <SelectItem value="7d" className="rounded-lg">
              Last 7 days
            </SelectItem>
          </SelectContent>
        </Select>
      </CardHeader>
      <CardContent className="px-2 pt-4 sm:px-6 sm:pt-6">
        <ChartContainer
          config={chartConfig}
          className="aspect-auto h-[250px] w-full"
        >
          <AreaChart data={filteredData}>
            <defs>
              <linearGradient id="fillThreats" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-threatsDetected)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-threatsDetected)"
                  stopOpacity={0.1}
                />
              </linearGradient>
              <linearGradient id="fillEmails" x1="0" y1="0" x2="0" y2="1">
                <stop
                  offset="5%"
                  stopColor="var(--color-emailsScanned)"
                  stopOpacity={0.8}
                />
                <stop
                  offset="95%"
                  stopColor="var(--color-emailsScanned)"
                  stopOpacity={0.1}
                />
              </linearGradient>
            </defs>
            <CartesianGrid vertical={false} strokeOpacity={0.1} />
            <XAxis
              dataKey="date"
              tickLine={false}
              axisLine={false}
              tickMargin={8}
              minTickGap={32}
              tickFormatter={(value) => {
                const date = new Date(value)
                return date.toLocaleDateString("en-US", {
                  month: "short",
                  day: "numeric",
                })
              }}
            />
            <ChartTooltip
              cursor={false}
              content={
                <ChartTooltipContent
                  labelFormatter={(value) => {
                    return new Date(value).toLocaleDateString("en-US", {
                      month: "short",
                      day: "numeric",
                    })
                  }}
                  indicator="dot"
                />
              }
            />
            <Area
              dataKey="threatsDetected"
              type="natural"
              fill="url(#fillThreats)"
              stroke="var(--color-threatsDetected)"
              stackId="a"
            />
            <Area
              dataKey="emailsScanned"
              type="natural"
              fill="url(#fillEmails)"
              stroke="var(--color-emailsScanned)"
              stackId="a"
            />
            <ChartLegend content={<ChartLegendContent />} />
          </AreaChart>
        </ChartContainer>
      </CardContent>
    </Card>
  )
}
