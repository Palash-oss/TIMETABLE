import { useState } from 'react'
import { Outlet, NavLink, useLocation } from 'react-router-dom'
import {
  LayoutGrid,
  Calendar,
  GraduationCap,
  Users,
  BookOpen,
  Building,
  UserCheck,
  Settings,
  Menu,
  X,
  Clock,
  ChevronRight
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const navigation = [
  { name: 'Dashboard', href: '/dashboard', icon: LayoutGrid },
  { name: 'Generate Timetable', href: '/generate', icon: Clock },
  { name: 'View Timetable', href: '/timetable', icon: Calendar },
  { name: 'Programs', href: '/programs', icon: GraduationCap },
  { name: 'Faculty', href: '/faculty', icon: Users },
  { name: 'Courses', href: '/courses', icon: BookOpen },
  { name: 'Rooms', href: '/rooms', icon: Building },
  { name: 'Students', href: '/students', icon: UserCheck },
  { name: 'Settings', href: '/settings', icon: Settings },
]

export default function Layout() {
  const [sidebarOpen, setSidebarOpen] = useState(false)
  const location = useLocation()

  const currentPage = navigation.find(item => item.href === location.pathname)?.name || 'Dashboard'

  return (
    <div className="flex min-h-screen bg-neutral-50 w-full">
      {/* Mobile sidebar backdrop */}
      <AnimatePresence>
        {sidebarOpen && (
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={() => setSidebarOpen(false)}
            className="fixed inset-0 bg-black/20 backdrop-blur-sm z-40 lg:hidden"
          />
        )}
      </AnimatePresence>

      {/* Sidebar */}
      <div
        className={`${
          sidebarOpen ? 'translate-x-0' : '-translate-x-full'
        } fixed inset-y-0 left-0 z-50 w-72 bg-white border-r border-neutral-100 transition-transform duration-300 ease-in-out lg:translate-x-0 lg:relative lg:flex`}
      >
        <div className="flex h-full flex-col w-72">
          {/* Logo */}
          <div className="flex h-16 items-center justify-between px-6 border-b border-neutral-100">
            <div className="flex items-center space-x-3">
              <div className="w-8 h-8 bg-primary-900 rounded-lg flex items-center justify-center">
                <Calendar className="w-5 h-5 text-white" />
              </div>
              <span className="text-lg font-semibold text-primary-900">TimeTable AI</span>
            </div>
            <button
              onClick={() => setSidebarOpen(false)}
              className="lg:hidden text-neutral-500 hover:text-primary-900"
            >
              <X className="w-5 h-5" />
            </button>
          </div>

          {/* Navigation */}
          <nav className="flex-1 space-y-1 px-3 py-4 overflow-y-auto">
            {navigation.map((item) => {
              const Icon = item.icon
              return (
                <NavLink
                  key={item.name}
                  to={item.href}
                  onClick={() => setSidebarOpen(false)}
                  className={({ isActive }) =>
                    `group flex items-center px-3 py-2.5 text-sm font-medium rounded-lg transition-all duration-200 ${
                      isActive
                        ? 'bg-primary-50 text-primary-900'
                        : 'text-neutral-600 hover:text-primary-900 hover:bg-neutral-50'
                    }`
                  }
                >
                  {({ isActive }) => (
                    <>
                      <Icon
                        className={`mr-3 h-5 w-5 transition-colors ${
                          isActive ? 'text-primary-900' : 'text-neutral-400 group-hover:text-primary-900'
                        }`}
                      />
                      {item.name}
                      {isActive && (
                        <ChevronRight className="ml-auto h-4 w-4 text-primary-900" />
                      )}
                    </>
                  )}
                </NavLink>
              )
            })}
          </nav>

          {/* Footer */}
          <div className="border-t border-neutral-100 px-6 py-4">
            <div className="text-xs text-neutral-500">
              <p>NEP 2020 Compliant</p>
              <p className="mt-1">Version 1.0.0</p>
            </div>
          </div>
        </div>
      </div>

      {/* Main content */}
      <div className="flex-1 flex flex-col min-w-0">
        {/* Top bar */}
        <header className="sticky top-0 z-30 bg-white border-b border-neutral-100 w-full">{/*...*/}
          <div className="flex h-16 items-center justify-between px-4 sm:px-6">
            <div className="flex items-center space-x-4">
              <button
                onClick={() => setSidebarOpen(true)}
                className="lg:hidden text-neutral-500 hover:text-primary-900"
              >
                <Menu className="w-6 h-6" />
              </button>
              <h1 className="text-xl font-semibold text-primary-900">{currentPage}</h1>
            </div>
            <div className="flex items-center space-x-4">
              <div className="flex items-center space-x-2">
                <span className="text-sm text-neutral-500">Academic Year:</span>
                <span className="text-sm font-medium text-primary-900">2024-25</span>
              </div>
              <div className="w-px h-6 bg-neutral-200" />
              <div className="flex items-center space-x-2">
                <span className="text-sm text-neutral-500">Semester:</span>
                <span className="text-sm font-medium text-primary-900">Odd</span>
              </div>
            </div>
          </div>
        </header>

        {/* Page content */}
        <main className="flex-1 p-4 sm:p-6 w-full">
          <Outlet />
        </main>
      </div>
    </div>
  )
}