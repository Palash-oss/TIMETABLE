import { motion } from 'framer-motion'
import {
  Calendar,
  Users,
  BookOpen,
  Building,
  Clock,
  TrendingUp,
  AlertCircle,
  CheckCircle
} from 'lucide-react'
import { useState, useEffect } from 'react'
import axios from 'axios'

const stats = [
  {
    name: 'Total Programs',
    value: '4',
    change: '+2',
    changeType: 'increase',
    icon: BookOpen,
    color: 'bg-blue-50 text-blue-600',
  },
  {
    name: 'Faculty Members',
    value: '48',
    change: '+5',
    changeType: 'increase',
    icon: Users,
    color: 'bg-green-50 text-green-600',
  },
  {
    name: 'Active Courses',
    value: '156',
    change: '+12',
    changeType: 'increase',
    icon: Calendar,
    color: 'bg-purple-50 text-purple-600',
  },
  {
    name: 'Available Rooms',
    value: '32',
    change: '0',
    changeType: 'neutral',
    icon: Building,
    color: 'bg-orange-50 text-orange-600',
  },
]

const recentActivities = [
  {
    id: 1,
    type: 'success',
    message: 'Timetable generated for B.Ed. Semester 3',
    time: '2 hours ago',
  },
  {
    id: 2,
    type: 'info',
    message: 'New faculty member Dr. Sarah Chen added',
    time: '5 hours ago',
  },
  {
    id: 3,
    type: 'warning',
    message: 'Room conflict detected in Lab 302',
    time: '1 day ago',
  },
  {
    id: 4,
    type: 'success',
    message: 'Successfully exported M.Ed. timetables',
    time: '2 days ago',
  },
]

export default function Dashboard() {
  const [loading, setLoading] = useState(false)

  const containerVariants = {
    hidden: { opacity: 0 },
    visible: {
      opacity: 1,
      transition: {
        staggerChildren: 0.1,
      },
    },
  }

  const itemVariants = {
    hidden: { y: 20, opacity: 0 },
    visible: {
      y: 0,
      opacity: 1,
      transition: {
        type: 'spring',
        stiffness: 100,
      },
    },
  }

  return (
    <motion.div
      variants={containerVariants}
      initial="hidden"
      animate="visible"
      className="space-y-6 w-full min-h-full"
    >
      {/* Welcome Section */}
      <motion.div variants={itemVariants} className="bg-white rounded-xl p-6 border border-neutral-100">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-semibold text-primary-900">Welcome back!</h2>
            <p className="text-neutral-600 mt-1">Here's an overview of your academic scheduling system</p>
          </div>
          <button className="btn btn-primary">
            <Clock className="w-4 h-4 mr-2" />
            Generate New Timetable
          </button>
        </div>
      </motion.div>

      {/* Stats Grid */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        {stats.map((stat, index) => {
          const Icon = stat.icon
          return (
            <motion.div
              key={stat.name}
              variants={itemVariants}
              className="card p-6 hover:shadow-md transition-shadow"
            >
              <div className="flex items-center justify-between">
                <div className="flex-1">
                  <p className="text-sm text-neutral-500">{stat.name}</p>
                  <p className="text-3xl font-semibold text-primary-900 mt-2">{stat.value}</p>
                  <div className="flex items-center mt-2">
                    <span
                      className={`text-sm font-medium ${
                        stat.changeType === 'increase'
                          ? 'text-green-600'
                          : stat.changeType === 'decrease'
                          ? 'text-red-600'
                          : 'text-neutral-500'
                      }`}
                    >
                      {stat.change}
                    </span>
                    <span className="text-sm text-neutral-400 ml-2">from last semester</span>
                  </div>
                </div>
                <div className={`p-3 rounded-lg ${stat.color}`}>
                  <Icon className="w-6 h-6" />
                </div>
              </div>
            </motion.div>
          )
        })}
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Recent Activities */}
        <motion.div variants={itemVariants} className="lg:col-span-2 card p-6">
          <h3 className="text-lg font-semibold text-primary-900 mb-4">Recent Activities</h3>
          <div className="space-y-4">
            {recentActivities.map((activity) => (
              <div key={activity.id} className="flex items-start space-x-3">
                {activity.type === 'success' ? (
                  <CheckCircle className="w-5 h-5 text-green-500 mt-0.5" />
                ) : activity.type === 'warning' ? (
                  <AlertCircle className="w-5 h-5 text-orange-500 mt-0.5" />
                ) : (
                  <div className="w-5 h-5 rounded-full bg-blue-100 mt-0.5" />
                )}
                <div className="flex-1">
                  <p className="text-sm text-primary-900">{activity.message}</p>
                  <p className="text-xs text-neutral-500 mt-1">{activity.time}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.div>

        {/* Quick Actions */}
        <motion.div variants={itemVariants} className="card p-6">
          <h3 className="text-lg font-semibold text-primary-900 mb-4">Quick Actions</h3>
          <div className="space-y-3">
            <button className="w-full btn btn-secondary text-sm justify-start">
              <Calendar className="w-4 h-4 mr-2" />
              View Current Timetable
            </button>
            <button className="w-full btn btn-secondary text-sm justify-start">
              <Users className="w-4 h-4 mr-2" />
              Manage Faculty
            </button>
            <button className="w-full btn btn-secondary text-sm justify-start">
              <BookOpen className="w-4 h-4 mr-2" />
              Add New Course
            </button>
            <button className="w-full btn btn-secondary text-sm justify-start">
              <Building className="w-4 h-4 mr-2" />
              Room Availability
            </button>
          </div>
        </motion.div>
      </div>

      {/* Optimization Score */}
      <motion.div variants={itemVariants} className="card p-6">
        <div className="flex items-center justify-between mb-4">
          <h3 className="text-lg font-semibold text-primary-900">Timetable Optimization Score</h3>
          <TrendingUp className="w-5 h-5 text-green-500" />
        </div>
        <div className="space-y-4">
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-600">Faculty Utilization</span>
              <span className="text-sm font-medium text-primary-900">87%</span>
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div className="bg-green-500 h-2 rounded-full" style={{ width: '87%' }} />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-600">Room Utilization</span>
              <span className="text-sm font-medium text-primary-900">76%</span>
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div className="bg-blue-500 h-2 rounded-full" style={{ width: '76%' }} />
            </div>
          </div>
          <div>
            <div className="flex items-center justify-between mb-2">
              <span className="text-sm text-neutral-600">Conflict Resolution</span>
              <span className="text-sm font-medium text-primary-900">100%</span>
            </div>
            <div className="w-full bg-neutral-200 rounded-full h-2">
              <div className="bg-purple-500 h-2 rounded-full" style={{ width: '100%' }} />
            </div>
          </div>
        </div>
      </motion.div>
    </motion.div>
  )
}