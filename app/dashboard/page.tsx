import type { Metadata } from "next"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs"
import DashboardHeader from "@/components/dashboard-header"
import CoursesList from "@/components/courses-list"
import OverviewStats from "@/components/overview-stats"
import RecentActivities from "@/components/recent-activities"

export const metadata: Metadata = {
  title: "Dashboard | University CMS",
  description: "Manage your courses and academic progress",
}

export default function DashboardPage() {
  return (
    <div className="flex min-h-screen flex-col">
      <DashboardHeader />

      <div className="container mx-auto py-6 px-4">
        <h1 className="text-3xl font-bold mb-6">Dashboard</h1>

        <Tabs defaultValue="overview" className="space-y-6">
          <TabsList className="grid w-full md:w-auto grid-cols-3 md:inline-flex">
            <TabsTrigger value="overview">Overview</TabsTrigger>
            <TabsTrigger value="courses">My Courses</TabsTrigger>
            <TabsTrigger value="activities">Recent Activities</TabsTrigger>
          </TabsList>

          <TabsContent value="overview" className="space-y-6">
            <OverviewStats />

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <Card>
                <CardHeader>
                  <CardTitle>Upcoming Deadlines</CardTitle>
                  <CardDescription>Your pending assignments and exams</CardDescription>
                </CardHeader>
                <CardContent>
                  <ul className="space-y-4">
                    <li className="flex justify-between items-center border-b pb-2">
                      <div>
                        <p className="font-medium">CS101 - Final Project</p>
                        <p className="text-sm text-gray-500">Computer Science Basics</p>
                      </div>
                      <div className="text-right">
                        <p className="text-red-500 font-medium">2 days left</p>
                        <p className="text-sm text-gray-500">25% of grade</p>
                      </div>
                    </li>
                    <li className="flex justify-between items-center border-b pb-2">
                      <div>
                        <p className="font-medium">MATH202 - Quiz 3</p>
                        <p className="text-sm text-gray-500">Advanced Calculus</p>
                      </div>
                      <div className="text-right">
                        <p className="text-amber-500 font-medium">5 days left</p>
                        <p className="text-sm text-gray-500">10% of grade</p>
                      </div>
                    </li>
                    <li className="flex justify-between items-center">
                      <div>
                        <p className="font-medium">ENG105 - Essay</p>
                        <p className="text-sm text-gray-500">Academic Writing</p>
                      </div>
                      <div className="text-right">
                        <p className="text-green-500 font-medium">2 weeks left</p>
                        <p className="text-sm text-gray-500">15% of grade</p>
                      </div>
                    </li>
                  </ul>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>Academic Progress</CardTitle>
                  <CardDescription>Current semester performance</CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">CS101 - Computer Science Basics</span>
                        <span className="text-sm font-medium">92%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{ width: "92%" }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">MATH202 - Advanced Calculus</span>
                        <span className="text-sm font-medium">78%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-blue-600 h-2 rounded-full" style={{ width: "78%" }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">ENG105 - Academic Writing</span>
                        <span className="text-sm font-medium">85%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-purple-600 h-2 rounded-full" style={{ width: "85%" }}></div>
                      </div>
                    </div>

                    <div>
                      <div className="flex justify-between mb-1">
                        <span className="text-sm font-medium">HIST101 - World History</span>
                        <span className="text-sm font-medium">90%</span>
                      </div>
                      <div className="w-full bg-gray-200 rounded-full h-2">
                        <div className="bg-green-600 h-2 rounded-full" style={{ width: "90%" }}></div>
                      </div>
                    </div>
                  </div>
                </CardContent>
              </Card>
            </div>
          </TabsContent>

          <TabsContent value="courses">
            <CoursesList />
          </TabsContent>

          <TabsContent value="activities">
            <RecentActivities />
          </TabsContent>
        </Tabs>
      </div>
    </div>
  )
}

