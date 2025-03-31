import Link from "next/link"
import { Button } from "@/components/ui/button"
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card"
import { BookOpen, GraduationCap, Users, BarChart4 } from "lucide-react"
import TestTailwind from "./test-tailwind"

export default function Home() {
  // Your existing code...

  return (
    <>
      <TestTailwind />
      <div className="flex flex-col min-h-screen">
        {/* Hero Section */}
        <header className="bg-gradient-to-r from-blue-600 to-violet-600 text-white py-20">
          <div className="container mx-auto px-4">
            <div className="max-w-3xl">
              <h1 className="text-4xl md:text-6xl font-bold mb-4">University Course Management System</h1>
              <p className="text-xl mb-8">
                Streamline your academic journey with our comprehensive course management solution
              </p>
              <div className="flex flex-wrap gap-4">
                <Button asChild size="lg" className="bg-white text-blue-600 hover:bg-gray-100">
                  <Link href="/auth/login">Login</Link>
                </Button>
                <Button
                  asChild
                  size="lg"
                  variant="outline"
                  className="bg-transparent border-white text-white hover:bg-white/10"
                >
                  <Link href="/auth/register">Register</Link>
                </Button>
              </div>
            </div>
          </div>
        </header>

        {/* Features Section */}
        <section className="py-16 bg-gray-50">
          <div className="container mx-auto px-4">
            <h2 className="text-3xl font-bold text-center mb-12">Key Features</h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
              <Card>
                <CardHeader>
                  <BookOpen className="h-10 w-10 text-blue-600 mb-2" />
                  <CardTitle>Course Management</CardTitle>
                  <CardDescription>Create, modify and track all your courses in one place</CardDescription>
                </CardHeader>
                <CardContent>
                  <p>Easily manage course materials, schedules, and assignments with our intuitive interface.</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <GraduationCap className="h-10 w-10 text-blue-600 mb-2" />
                  <CardTitle>Student Enrollment</CardTitle>
                  <CardDescription>Streamlined process for course registration</CardDescription>
                </CardHeader>
                <CardContent>
                  <p>
                    Students can browse available courses, view prerequisites, and enroll with blockchain verification.
                  </p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <Users className="h-10 w-10 text-blue-600 mb-2" />
                  <CardTitle>Faculty Portal</CardTitle>
                  <CardDescription>Dedicated tools for professors and instructors</CardDescription>
                </CardHeader>
                <CardContent>
                  <p>Manage student performance, upload materials, and communicate with your class efficiently.</p>
                </CardContent>
              </Card>

              <Card>
                <CardHeader>
                  <BarChart4 className="h-10 w-10 text-blue-600 mb-2" />
                  <CardTitle>Analytics Dashboard</CardTitle>
                  <CardDescription>Insights into performance and engagement</CardDescription>
                </CardHeader>
                <CardContent>
                  <p>Get detailed analytics on course participation, student progress, and academic outcomes.</p>
                </CardContent>
              </Card>
            </div>
          </div>
        </section>

        {/* Blockchain Integration Section */}
        <section className="py-16 bg-white">
          <div className="container mx-auto px-4">
            <div className="flex flex-col md:flex-row items-center gap-12">
              <div className="md:w-1/2">
                <h2 className="text-3xl font-bold mb-6">Powered by Algorand Blockchain</h2>
                <p className="text-lg mb-4">
                  Our system leverages Algorand's secure and efficient blockchain technology for:
                </p>
                <ul className="space-y-2">
                  <li className="flex items-start">
                    <div className="rounded-full bg-green-100 p-1 mr-3 mt-1">
                      <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span>Secure course certification and degree verification</span>
                  </li>
                  <li className="flex items-start">
                    <div className="rounded-full bg-green-100 p-1 mr-3 mt-1">
                      <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span>Transparent and immutable academic records</span>
                  </li>
                  <li className="flex items-start">
                    <div className="rounded-full bg-green-100 p-1 mr-3 mt-1">
                      <svg className="h-4 w-4 text-green-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth="2" d="M5 13l4 4L19 7" />
                      </svg>
                    </div>
                    <span>Efficient payment processing for tuition and fees</span>
                  </li>
                </ul>
                <Button className="mt-6 bg-blue-600 hover:bg-blue-700">
                  <Link href="/about/blockchain">Learn More</Link>
                </Button>
              </div>
              <div className="md:w-1/2">
                <div className="rounded-lg bg-gray-100 p-6 border border-gray-200">
                  <h3 className="text-xl font-semibold mb-4">Smart Contract Sample</h3>
                  <pre className="bg-gray-900 text-gray-100 p-4 rounded text-sm overflow-x-auto">
                    <code>
                      {`# Algorand Smart Contract (PyTeal)
def approval_program():
    # Handle course registration
    on_register = Seq([
        App.globalPut(Bytes("student_count"), 
                     App.globalGet(Bytes("student_count")) + Int(1)),
        App.localPut(Int(0), Bytes("enrolled"), Int(1)),
        App.localPut(Int(0), Bytes("timestamp"), Global.latest_timestamp()),
        Return(Int(1))
    ])
    
    program = Cond(
        [Txn.application_id() == Int(0), Return(Int(1))],
        [Txn.on_completion() == OnComplete.DeleteApplication, Return(Int(0))],
        [Txn.on_completion() == OnComplete.UpdateApplication, Return(Int(0))],
        [Txn.on_completion() == OnComplete.CloseOut, Return(Int(1))],
        [Txn.on_completion() == OnComplete.OptIn, Return(Int(1))],
        [Txn.application_args[0] == Bytes("register"), on_register]
    )
    return program`}
                    </code>
                  </pre>
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* Footer */}
        <footer className="bg-gray-800 text-white py-12 mt-auto">
          <div className="container mx-auto px-4">
            <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
              <div>
                <h3 className="text-xl font-bold mb-4">University CMS</h3>
                <p className="text-gray-300">
                  A complete solution for educational institutions to manage courses, students, and academic processes.
                </p>
              </div>
              <div>
                <h4 className="text-lg font-semibold mb-4">Quick Links</h4>
                <ul className="space-y-2">
                  <li>
                    <Link href="/courses" className="text-gray-300 hover:text-white">
                      Courses
                    </Link>
                  </li>
                  <li>
                    <Link href="/auth/login" className="text-gray-300 hover:text-white">
                      Login
                    </Link>
                  </li>
                  <li>
                    <Link href="/auth/register" className="text-gray-300 hover:text-white">
                      Register
                    </Link>
                  </li>
                  <li>
                    <Link href="/about" className="text-gray-300 hover:text-white">
                      About
                    </Link>
                  </li>
                </ul>
              </div>
              <div>
                <h4 className="text-lg font-semibold mb-4">Contact</h4>
                <p className="text-gray-300">Email: support@universitycms.com</p>
                <p className="text-gray-300">Phone: (555) 123-4567</p>
              </div>
            </div>
            <div className="border-t border-gray-700 mt-8 pt-8 text-center text-gray-400">
              <p>© {new Date().getFullYear()} University Course Management System. All rights reserved.</p>
            </div>
          </div>
        </footer>
      </div>
    </>
  )
}

