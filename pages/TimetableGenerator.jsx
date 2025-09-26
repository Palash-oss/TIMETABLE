import { useState } from 'react'
import { motion } from 'framer-motion'
import {
  Calendar,
  Settings,
  Download,
  Play,
  AlertTriangle,
  CheckCircle,
  Clock,
  Loader,
  FileDown
} from 'lucide-react'
import Select from 'react-select'
import axios from 'axios'
import toast from 'react-hot-toast'

const customSelectStyles = {
  control: (base) => ({
    ...base,
    borderColor: '#e5e7eb',
    '&:hover': {
      borderColor: '#d1d5db',
    },
    '&:focus': {
      borderColor: '#6b7280',
      boxShadow: '0 0 0 2px rgba(107, 114, 128, 0.1)',
    },
  }),
  option: (base, state) => ({
    ...base,
    backgroundColor: state.isSelected ? '#f3f4f6' : state.isFocused ? '#f9fafb' : 'white',
    color: '#111827',
  }),
}

export default function TimetableGenerator() {
  const [generating, setGenerating] = useState(false)
  const [progress, setProgress] = useState(0)
  const [formData, setFormData] = useState({
    semester: '',
    academicYear: '2024-25',
    programs: [],
    optimizeFor: 'balanced',
    respectConstraints: true,
  })

  const programOptions = [
    { value: 'bed', label: 'B.Ed. - Bachelor of Education' },
    { value: 'med', label: 'M.Ed. - Master of Education' },
    { value: 'fyup', label: 'FYUP - Four Year Undergraduate Program' },
    { value: 'itep', label: 'ITEP - Integrated Teacher Education Program' },
  ]

  const optimizationOptions = [
    { value: 'balanced', label: 'Balanced', description: 'Equal priority to all factors' },
    { value: 'minimal_gaps', label: 'Minimal Gaps', description: 'Reduce free periods for students' },
    { value: 'faculty_preference', label: 'Faculty Preference', description: 'Prioritize faculty availability' },
    { value: 'room_optimization', label: 'Room Optimization', description: 'Maximize room utilization' },
  ]

  const handleGenerate = async () => {
    if (!formData.programs.length) {
      toast.error('Please select at least one program')
      return
    }
    if (!formData.semester) {
      toast.error('Please select a semester')
      return
    }

    setGenerating(true)
    setProgress(0)

    // Simulate progress
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 90) {
          clearInterval(interval)
          return 90
        }
        return prev + 10
      })
    }, 500)

    try {
      const response = await axios.post('/api/generate-timetable', {
        semester: formData.semester,
        academic_year: formData.academicYear,
        program_ids: formData.programs.map(p => p.value),
        respect_constraints: formData.respectConstraints,
        optimize_for: formData.optimizeFor,
      })

      if (response.data.success) {
        setProgress(100)
        toast.success('Timetable generated successfully!')
        setTimeout(() => {
          setGenerating(false)
          setProgress(0)
        }, 1000)
      }
    } catch (error) {
      toast.error('Failed to generate timetable. Please try again.')
      setGenerating(false)
      setProgress(0)
    }
  }

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="bg-white rounded-xl p-6 border border-neutral-100">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-xl font-semibold text-primary-900">AI-Powered Timetable Generation</h2>
            <p className="text-neutral-600 mt-1">Configure parameters for optimal schedule generation</p>
          </div>
          <div className="flex items-center space-x-2 text-sm text-neutral-500">
            <Clock className="w-4 h-4" />
            <span>Estimated time: 2-3 minutes</span>
          </div>
        </div>
      </div>

      {/* Configuration Form */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <div className="lg:col-span-2 space-y-6">
          {/* Basic Settings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-primary-900 mb-4">Basic Configuration</h3>
            
            <div className="space-y-4">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div>
                  <label className="label">Academic Year</label>
                  <input
                    type="text"
                    className="input"
                    value={formData.academicYear}
                    onChange={(e) => setFormData({ ...formData, academicYear: e.target.value })}
                  />
                </div>
                <div>
                  <label className="label">Semester</label>
                  <select
                    className="input"
                    value={formData.semester}
                    onChange={(e) => setFormData({ ...formData, semester: e.target.value })}
                  >
                    <option value="">Select Semester</option>
                    <option value="Odd">Odd Semester</option>
                    <option value="Even">Even Semester</option>
                  </select>
                </div>
              </div>

              <div>
                <label className="label">Select Programs</label>
                <Select
                  isMulti
                  options={programOptions}
                  value={formData.programs}
                  onChange={(value) => setFormData({ ...formData, programs: value })}
                  styles={customSelectStyles}
                  placeholder="Choose programs to generate timetable for..."
                  className="text-sm"
                />
              </div>
            </div>
          </motion.div>

          {/* Optimization Settings */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.1 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-primary-900 mb-4">Optimization Settings</h3>
            
            <div className="space-y-4">
              <div>
                <label className="label">Optimization Priority</label>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
                  {optimizationOptions.map((option) => (
                    <label
                      key={option.value}
                      className={`flex items-start space-x-3 p-3 border rounded-lg cursor-pointer transition-all ${
                        formData.optimizeFor === option.value
                          ? 'border-primary-500 bg-primary-50'
                          : 'border-neutral-200 hover:border-neutral-300'
                      }`}
                    >
                      <input
                        type="radio"
                        name="optimization"
                        value={option.value}
                        checked={formData.optimizeFor === option.value}
                        onChange={(e) => setFormData({ ...formData, optimizeFor: e.target.value })}
                        className="mt-0.5"
                      />
                      <div className="flex-1">
                        <p className="text-sm font-medium text-primary-900">{option.label}</p>
                        <p className="text-xs text-neutral-500 mt-0.5">{option.description}</p>
                      </div>
                    </label>
                  ))}
                </div>
              </div>

              <div className="flex items-center space-x-3">
                <input
                  type="checkbox"
                  id="constraints"
                  checked={formData.respectConstraints}
                  onChange={(e) => setFormData({ ...formData, respectConstraints: e.target.checked })}
                  className="w-4 h-4 text-primary-600 rounded border-neutral-300 focus:ring-primary-500"
                />
                <label htmlFor="constraints" className="text-sm text-primary-900">
                  Respect all hard constraints (faculty availability, room capacity, etc.)
                </label>
              </div>
            </div>
          </motion.div>

          {/* Generation Progress */}
          {generating && (
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="card p-6"
            >
              <div className="flex items-center justify-between mb-4">
                <h3 className="text-lg font-semibold text-primary-900">Generating Timetable</h3>
                <Loader className="w-5 h-5 text-primary-600 animate-spin" />
              </div>
              
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm">
                  <span className="text-neutral-600">Progress</span>
                  <span className="font-medium text-primary-900">{progress}%</span>
                </div>
                <div className="w-full bg-neutral-200 rounded-full h-2">
                  <motion.div
                    className="bg-primary-600 h-2 rounded-full"
                    initial={{ width: 0 }}
                    animate={{ width: `${progress}%` }}
                    transition={{ duration: 0.5 }}
                  />
                </div>
                
                <div className="space-y-2 mt-4">
                  <div className="flex items-center space-x-2 text-sm">
                    {progress >= 20 ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : (
                      <Loader className="w-4 h-4 text-neutral-400 animate-spin" />
                    )}
                    <span className={progress >= 20 ? 'text-primary-900' : 'text-neutral-500'}>
                      Loading course data
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    {progress >= 40 ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : progress >= 20 ? (
                      <Loader className="w-4 h-4 text-neutral-400 animate-spin" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border-2 border-neutral-300" />
                    )}
                    <span className={progress >= 40 ? 'text-primary-900' : 'text-neutral-500'}>
                      Checking constraints
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    {progress >= 60 ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : progress >= 40 ? (
                      <Loader className="w-4 h-4 text-neutral-400 animate-spin" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border-2 border-neutral-300" />
                    )}
                    <span className={progress >= 60 ? 'text-primary-900' : 'text-neutral-500'}>
                      Optimizing schedule
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    {progress >= 80 ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : progress >= 60 ? (
                      <Loader className="w-4 h-4 text-neutral-400 animate-spin" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border-2 border-neutral-300" />
                    )}
                    <span className={progress >= 80 ? 'text-primary-900' : 'text-neutral-500'}>
                      Resolving conflicts
                    </span>
                  </div>
                  <div className="flex items-center space-x-2 text-sm">
                    {progress === 100 ? (
                      <CheckCircle className="w-4 h-4 text-green-500" />
                    ) : progress >= 80 ? (
                      <Loader className="w-4 h-4 text-neutral-400 animate-spin" />
                    ) : (
                      <div className="w-4 h-4 rounded-full border-2 border-neutral-300" />
                    )}
                    <span className={progress === 100 ? 'text-primary-900' : 'text-neutral-500'}>
                      Finalizing timetable
                    </span>
                  </div>
                </div>
              </div>
            </motion.div>
          )}
        </div>

        {/* Sidebar */}
        <div className="space-y-6">
          {/* Action Buttons */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.2 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-primary-900 mb-4">Actions</h3>
            
            <div className="space-y-3">
              <button
                onClick={handleGenerate}
                disabled={generating}
                className="w-full btn btn-primary"
              >
                {generating ? (
                  <>
                    <Loader className="w-4 h-4 mr-2 animate-spin" />
                    Generating...
                  </>
                ) : (
                  <>
                    <Play className="w-4 h-4 mr-2" />
                    Generate Timetable
                  </>
                )}
              </button>
              
              <button className="w-full btn btn-secondary">
                <Settings className="w-4 h-4 mr-2" />
                Advanced Settings
              </button>
            </div>
          </motion.div>

          {/* Information */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-primary-900 mb-4">Information</h3>
            
            <div className="space-y-3 text-sm">
              <div className="flex items-start space-x-2">
                <AlertTriangle className="w-4 h-4 text-orange-500 mt-0.5 flex-shrink-0" />
                <p className="text-neutral-600">
                  Ensure all faculty assignments and room allocations are updated before generating.
                </p>
              </div>
              
              <div className="flex items-start space-x-2">
                <CheckCircle className="w-4 h-4 text-green-500 mt-0.5 flex-shrink-0" />
                <p className="text-neutral-600">
                  The AI algorithm will automatically resolve conflicts and optimize based on your preferences.
                </p>
              </div>
            </div>
          </motion.div>

          {/* Export Options */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.4 }}
            className="card p-6"
          >
            <h3 className="text-lg font-semibold text-primary-900 mb-4">Export Options</h3>
            
            <div className="space-y-2">
              <button className="w-full btn btn-secondary text-sm justify-start">
                <FileDown className="w-4 h-4 mr-2" />
                Export as PDF
              </button>
              <button className="w-full btn btn-secondary text-sm justify-start">
                <FileDown className="w-4 h-4 mr-2" />
                Export as Excel
              </button>
            </div>
          </motion.div>
        </div>
      </div>
    </div>
  )
}