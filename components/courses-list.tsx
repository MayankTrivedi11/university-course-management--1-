import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from "@/components/ui/card"
import { Badge } from "@/components/ui/badge"
import { BookOpen, Calendar, Clock, MoreHorizontal, Users } from "lucide-react"
import Link from "next/link"
import { DropdownMenu, DropdownMenuContent, DropdownMenuItem, DropdownMenuTrigger } from "@/components/ui/dropdown-menu"

export default function CoursesList() {
  return (
    <div className="grid gap-6">
      <div className="flex justify-between items-center">
        <h2 className="text-2xl font-bold">My Courses</h2>
        <Link href="/courses">
          <Button variant="outline">Browse All Courses</Button>
        </Link>
      </div>

      <div className="grid grid-cols-1 gap-6">
        {enrolledCourses.map((course) => (
          <Card key={course.id} className="overflow-hidden">
            <div className="flex flex-col md:flex-row">
              <div className="w-full md:w-2 shrink-0" style={{ backgroundColor: course.color }}></div>
              <div className="flex-1 p-0">
                <CardHeader className="flex flex-row items-start justify-between">
                  <div>
                    <div className="flex items-center gap-2">
                      <CardTitle>{course.title}</CardTitle>
                      <Badge
                        variant={
                          course.progress === "Completed"
                            ? "success"
                            : course.progress === "In Progress"
                              ? "default"
                              : "outline"
                        }
                      >
                        {course.progress}
                      </Badge>
                    </div>
                    <CardDescription>
                      {course.code} • {course.instructor}
                    </CardDescription>
                  </div>

                  <DropdownMenu>
                    <DropdownMenuTrigger asChild>
                      <Button variant="ghost" size="icon">
                        <MoreHorizontal className="h-4 w-4" />
                        <span className="sr-only">Menu</span>
                      </Button>
                    </DropdownMenuTrigger>
                    <DropdownMenuContent align="end">
                      <DropdownMenuItem>View Course</DropdownMenuItem>
                      <DropdownMenuItem>View Syllabus</DropdownMenuItem>
                      <DropdownMenuItem>Contact Instructor</DropdownMenuItem>
                      <DropdownMenuItem>Unenroll</DropdownMenuItem>
                    </DropdownMenuContent>
                  </DropdownMenu>
                </CardHeader>

                <CardContent>
                  <div className="grid gap-2">
                    <div className="text-sm">{course.description}</div>

                    <div className="mt-2 grid grid-cols-2 md:grid-cols-4 gap-3">
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Calendar className="h-4 w-4" />
                        <span>{course.term}</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Clock className="h-4 w-4" />
                        <span>{course.credits} credits</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <Users className="h-4 w-4" />
                        <span>{course.students} students</span>
                      </div>
                      <div className="flex items-center gap-2 text-sm text-muted-foreground">
                        <BookOpen className="h-4 w-4" />
                        <span>{course.lessons} lessons</span>
                      </div>
                    </div>

                    <div className="mt-4">
                      <div className="flex justify-between text-sm">
                        <span>Progress</span>
                        <span>{course.completedPercentage}%</span>
                      </div>
                      <div className="mt-1 w-full bg-gray-200 rounded-full h-2">
                        <div
                          className="h-2 rounded-full"
                          style={{
                            width: `${course.completedPercentage}%`,
                            backgroundColor: course.color,
                          }}
                        ></div>
                      </div>
                    </div>
                  </div>
                </CardContent>

                <CardFooter className="flex justify-between">
                  <div className="text-sm">
                    <span className="font-medium">Next Session:</span> {course.nextSession}
                  </div>
                  <Button asChild>
                    <Link href={`/courses/${course.id}`}>Continue Learning</Link>
                  </Button>
                </CardFooter>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </div>
  )
}

const enrolledCourses = [
  {
    id: 1,
    title: "Introduction to Computer Science",
    code: "CS101",
    instructor: "Dr. Alan Turing",
    description:
      "An introduction to computer science and programming with Python, covering basic algorithms and data structures.",
    term: "Fall 2023",
    credits: 3,
    students: 42,
    lessons: 24,
    progress: "In Progress",
    completedPercentage: 75,
    nextSession: "Tuesday, 10:00 AM - Lecture Hall A",
    color: "#3b82f6", // blue-500
  },
  {
    id: 2,
    title: "Advanced Calculus",
    code: "MATH202",
    instructor: "Dr. Katherine Johnson",
    description:
      "Delves into multivariable calculus, vector calculus, and their applications in physics and engineering.",
    term: "Fall 2023",
    credits: 4,
    students: 28,
    lessons: 32,
    progress: "In Progress",
    completedPercentage: 60,
    nextSession: "Wednesday, 2:00 PM - Math Center B",
    color: "#8b5cf6", // violet-500
  },
  {
    id: 3,
    title: "Academic Writing",
    code: "ENG105",
    instructor: "Prof. Emily Dickinson",
    description: "Learn to write clear, concise, and well-organized academic papers across different disciplines.",
    term: "Fall 2023",
    credits: 3,
    students: 35,
    lessons: 18,
    progress: "Behind",
    completedPercentage: 30,
    nextSession: "Thursday, 11:00 AM - Humanities Building 202",
    color: "#ec4899", // pink-500
  },
]

