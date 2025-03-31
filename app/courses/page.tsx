import { Button } from "@/components/ui/button"
import { Card, CardContent, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Input } from "@/components/ui/input"
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select"
import Link from "next/link"
import { Clock, Users } from "lucide-react"
import DashboardHeader from "@/components/dashboard-header"

export default function CoursesPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <DashboardHeader />

      <div className="container mx-auto py-6 px-4">
        <div className="flex flex-col md:flex-row gap-4 justify-between items-start md:items-center mb-6">
          <div>
            <h1 className="text-3xl font-bold">Course Catalog</h1>
            <p className="text-gray-500">Browse and enroll in available courses</p>
          </div>

          <div className="w-full md:w-auto flex flex-col md:flex-row gap-3">
            <Input placeholder="Search courses..." className="md:w-64" />
            <Select defaultValue="all">
              <SelectTrigger className="w-full md:w-40">
                <SelectValue placeholder="Filter by department" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="all">All Departments</SelectItem>
                <SelectItem value="cs">Computer Science</SelectItem>
                <SelectItem value="math">Mathematics</SelectItem>
                <SelectItem value="eng">English</SelectItem>
                <SelectItem value="hist">History</SelectItem>
                <SelectItem value="sci">Science</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {courses.map((course) => (
            <Card key={course.id} className="flex flex-col">
              <CardHeader className="pb-3">
                <div className="flex justify-between items-start">
                  <div className="flex items-center gap-2">
                    <div className={`w-3 h-3 rounded-full ${getStatusColor(course.status)}`} />
                    <span className="text-sm text-gray-500">{course.code}</span>
                  </div>
                  <span className={`text-xs font-medium px-2 py-1 rounded ${getStatusBadge(course.status)}`}>
                    {course.status}
                  </span>
                </div>
                <CardTitle className="text-xl">{course.title}</CardTitle>
                <p className="text-sm text-gray-500">{course.department}</p>
              </CardHeader>
              <CardContent className="flex-grow">
                <p className="text-sm text-gray-700 mb-4">{course.description}</p>
                <div className="grid grid-cols-2 gap-2 text-sm">
                  <div className="flex items-center gap-1.5">
                    <Users className="h-4 w-4 text-gray-500" />
                    <span>{course.enrollment} students</span>
                  </div>
                  <div className="flex items-center gap-1.5">
                    <Clock className="h-4 w-4 text-gray-500" />
                    <span>{course.credits} credits</span>
                  </div>
                </div>
              </CardContent>
              <CardFooter className="pt-3 border-t">
                <div className="w-full flex justify-between items-center">
                  <p className="font-semibold">${course.fee}</p>
                  <Button
                    asChild
                    variant={course.status === "Full" ? "outline" : "default"}
                    disabled={course.status === "Full"}
                  >
                    <Link href={`/courses/${course.id}`}>
                      {course.status === "Full" ? "Join Waitlist" : "Enroll Now"}
                    </Link>
                  </Button>
                </div>
              </CardFooter>
            </Card>
          ))}
        </div>

        <div className="mt-8 flex justify-center">
          <div className="flex items-center gap-2">
            <Button variant="outline" size="sm" disabled>
              Previous
            </Button>
            <Button variant="outline" size="sm" className="bg-primary text-primary-foreground">
              1
            </Button>
            <Button variant="outline" size="sm">
              2
            </Button>
            <Button variant="outline" size="sm">
              3
            </Button>
            <Button variant="outline" size="sm">
              Next
            </Button>
          </div>
        </div>
      </div>
    </div>
  )
}

function getStatusColor(status: string) {
  switch (status) {
    case "Open":
      return "bg-green-500"
    case "Closing Soon":
      return "bg-yellow-500"
    case "Full":
      return "bg-red-500"
    default:
      return "bg-gray-500"
  }
}

function getStatusBadge(status: string) {
  switch (status) {
    case "Open":
      return "bg-green-100 text-green-800"
    case "Closing Soon":
      return "bg-yellow-100 text-yellow-800"
    case "Full":
      return "bg-red-100 text-red-800"
    default:
      return "bg-gray-100 text-gray-800"
  }
}

const courses = [
  {
    id: 1,
    code: "CS101",
    title: "Introduction to Computer Science",
    department: "Computer Science",
    description: "Fundamental concepts of computer science and programming with Python.",
    enrollment: 42,
    credits: 3,
    fee: 350,
    status: "Open",
  },
  {
    id: 2,
    code: "MATH202",
    title: "Advanced Calculus",
    department: "Mathematics",
    description: "In-depth study of calculus concepts including limits, derivatives, and integrals.",
    enrollment: 28,
    credits: 4,
    fee: 400,
    status: "Open",
  },
  {
    id: 3,
    code: "ENG105",
    title: "Academic Writing",
    department: "English",
    description: "Learn to write clear, concise, and well-organized academic papers.",
    enrollment: 35,
    credits: 3,
    fee: 320,
    status: "Closing Soon",
  },
  {
    id: 4,
    code: "HIST101",
    title: "World History",
    department: "History",
    description: "Survey of major historical events and developments across global civilizations.",
    enrollment: 50,
    credits: 3,
    fee: 320,
    status: "Full",
  },
  {
    id: 5,
    code: "BIO205",
    title: "Human Anatomy",
    department: "Biology",
    description: "Study of the structure of the human body and its systems.",
    enrollment: 32,
    credits: 4,
    fee: 450,
    status: "Open",
  },
  {
    id: 6,
    code: "PHYS101",
    title: "Physics I",
    department: "Physics",
    description: "Introduction to mechanics, energy, and thermodynamics.",
    enrollment: 25,
    credits: 4,
    fee: 420,
    status: "Closing Soon",
  },
]

