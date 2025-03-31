import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { FileText, MessageSquare, BookOpen, AlertCircle } from "lucide-react"

export default function RecentActivities() {
  return (
    <Card>
      <CardHeader>
        <CardTitle>Recent Activities</CardTitle>
        <CardDescription>Your latest actions and notifications</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-6">
          {activities.map((activity, index) => (
            <div key={index} className="flex items-start gap-4">
              <div className={`rounded-full p-2 ${getActivityIconBg(activity.type)}`}>
                {getActivityIcon(activity.type)}
              </div>
              <div className="grid gap-1">
                <p className="text-sm font-medium">{activity.title}</p>
                <p className="text-sm text-muted-foreground">{activity.description}</p>
                <p className="text-xs text-muted-foreground">{activity.time}</p>
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  )
}

function getActivityIcon(type: string) {
  switch (type) {
    case "submission":
      return <FileText className="h-4 w-4 text-white" />
    case "discussion":
      return <MessageSquare className="h-4 w-4 text-white" />
    case "course":
      return <BookOpen className="h-4 w-4 text-white" />
    case "deadline":
      return <AlertCircle className="h-4 w-4 text-white" />
    default:
      return <FileText className="h-4 w-4 text-white" />
  }
}

function getActivityIconBg(type: string) {
  switch (type) {
    case "submission":
      return "bg-blue-500"
    case "discussion":
      return "bg-green-500"
    case "course":
      return "bg-purple-500"
    case "deadline":
      return "bg-red-500"
    default:
      return "bg-gray-500"
  }
}

const activities = [
  {
    type: "submission",
    title: "Assignment Submitted",
    description: "You submitted your CS101 final project",
    time: "Today at 10:32 AM",
  },
  {
    type: "discussion",
    title: "New Discussion Reply",
    description: "Prof. Turing replied to your question in CS101",
    time: "Yesterday at 5:45 PM",
  },
  {
    type: "course",
    title: "Course Material Updated",
    description: "New lecture notes available in MATH202",
    time: "Yesterday at 3:15 PM",
  },
  {
    type: "deadline",
    title: "Upcoming Deadline",
    description: "ENG105 essay due in 2 days",
    time: "Mar 20, 2023",
  },
  {
    type: "submission",
    title: "Assignment Graded",
    description: "Your MATH202 homework was graded: 92/100",
    time: "Mar 18, 2023",
  },
]

