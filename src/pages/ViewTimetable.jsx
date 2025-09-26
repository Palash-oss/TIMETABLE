import { useState, useEffect } from 'react'
import { motion } from 'framer-motion'
import {
  Calendar,
  Download,
  Filter,
  Search,
  ChevronDown,
  Clock,
  MapPin,
  User,
  BookOpen,
  FileDown,
  Loader,
  AlertCircle
} from 'lucide-react'
import { timetableAPI, programsAPI } from '../services/api'
import toast from 'react-hot-toast'

const timeSlots = [
  '9:00 - 10:00',
  '10:00 - 11:00',
  '11:00 - 12:00',
  '12:00 - 13:00',
  '14:00 - 15:00',
  '15:00 - 16:00',
  '16:00 - 17:00'
]

const days = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday']

export default function ViewTimetable() {
  const [selectedProgram, setSelectedProgram] = useState('1')
  const [selectedSemester, setSelectedSemester] = useState('1')
  const [selectedSection, setSelectedSection] = useState('A')
  const [timetable, setTimetable] = useState({})
  const [programs, setPrograms] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)
  const [lastGenerated, setLastGenerated] = useState(null)

  // Load programs on component mount
  useEffect(() => {
    const loadPrograms = async () => {
      try {
        const response = await programsAPI.getAll()
        if (response.data.programs && response.data.programs.length > 0) {
          setPrograms(response.data.programs)
          setSelectedProgram(response.data.programs[0].id.toString())
        }
      } catch (error) {
        console.error('Failed to load programs:', error)
        toast.error('Failed to load programs')
      }
    }
    
    loadPrograms()
  }, [])

  // Load timetable when program or semester changes
  useEffect(() => {
    if (selectedProgram && selectedSemester) {
      loadTimetable()
    }
  }, [selectedProgram, selectedSemester])

  const loadTimetable = async () => {
    setLoading(true)
    setError(null)
    
    try {
      // Try to generate a fresh timetable to get the latest data
      const response = await timetableAPI.generate({
        program_id: parseInt(selectedProgram),
        semester: parseInt(selectedSemester),
      })

      if (response.data.success && response.data.timetable) {
        // Convert the API response format to the expected format
        const formattedTimetable = {}
        
        Object.keys(response.data.timetable).forEach(day => {
          formattedTimetable[day] = {}
          response.data.timetable[day].forEach(slot => {
            formattedTimetable[day][slot.time] = {
              course: slot.subject_name,
              faculty: slot.teacher,
              room: slot.classroom,
              code: slot.subject_code,
              credits: slot.credits,
              category: slot.nep_category
            }
          })
        })
        
        setTimetable(formattedTimetable)
        setLastGenerated(new Date().toLocaleString())
      } else {
        setError('No timetable available for the selected program and semester')
        setTimetable({})
      }
    } catch (error) {
      console.error('Failed to load timetable:', error)
      setError('Failed to load timetable. Please try again.')
      setTimetable({})
      toast.error('Failed to load timetable')
    } finally {
      setLoading(false)
    }
  }

  const exportTimetable = (format) => {
    // Implement export functionality
    console.log(`Exporting timetable as ${format}`)
  }

  return (
    <div className="space-y-6 w-full min-h-full">
      {/* Header Section */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-2xl font-bold text-primary-900">View Timetable</h1>
          <p className="text-neutral-600 mt-1">View and export generated timetables for different programs</p>
        </div>
        
        <div className="flex items-center space-x-3">
          <button
            onClick={() => exportTimetable('PDF')}
            className="btn btn-secondary flex items-center space-x-2"
          >
            <FileDown className="w-4 h-4" />
            <span>Export PDF</span>
          </button>
          <button
            onClick={() => exportTimetable('Excel')}
            className="btn btn-primary flex items-center space-x-2"
          >
            <Download className="w-4 h-4" />
            <span>Export Excel</span>
          </button>
        </div>
      </div>

      {/* Filters Section */}
      <div className="card p-6">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <div>
            <label className="label">Program</label>
            <select 
              value={selectedProgram}
              onChange={(e) => setSelectedProgram(e.target.value)}
              className="input"
              disabled={loading}
            >
              {programs.map(program => (
                <option key={program.id} value={program.id}>
                  {program.name} ({program.code})
                </option>
              ))}
            </select>
          </div>
          
          <div>
            <label className="label">Semester</label>
            <select 
              value={selectedSemester}
              onChange={(e) => setSelectedSemester(e.target.value)}
              className="input"
              disabled={loading}
            >
              {Array.from({length: 8}, (_, i) => (
                <option key={i+1} value={i+1}>Semester {i+1}</option>
              ))}
            </select>
          </div>
          
          <div className="flex items-end">
            <button
              onClick={loadTimetable}
              disabled={loading}
              className="btn btn-primary flex items-center space-x-2 w-full"
            >
              {loading ? (
                <Loader className="w-4 h-4 animate-spin" />
              ) : (
                <Calendar className="w-4 h-4" />
              )}
              <span>{loading ? 'Loading...' : 'Refresh Timetable'}</span>
            </button>
          </div>
        </div>
        
        {lastGenerated && (
          <div className="mt-4 text-sm text-neutral-600 flex items-center space-x-1">
            <Clock className="w-4 h-4" />
            <span>Last updated: {lastGenerated}</span>
          </div>
        )}
      </div>

      {/* Timetable Grid */}
      <div className="card p-6">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-xl font-semibold text-primary-900">
            {programs.find(p => p.id.toString() === selectedProgram)?.name || 'Program'} - Semester {selectedSemester}
          </h2>
          {lastGenerated && (
            <div className="flex items-center space-x-2 text-sm text-neutral-600">
              <Calendar className="w-4 h-4" />
              <span>Generated: {lastGenerated}</span>
            </div>
          )}
        </div>

        {loading ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Loader className="w-8 h-8 animate-spin mx-auto mb-2 text-primary-600" />
              <p className="text-neutral-600">Loading timetable...</p>
            </div>
          </div>
        ) : error ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <AlertCircle className="w-8 h-8 mx-auto mb-2 text-red-500" />
              <p className="text-red-600 mb-4">{error}</p>
              <button
                onClick={loadTimetable}
                className="btn btn-primary"
              >
                Try Again
              </button>
            </div>
          </div>
        ) : Object.keys(timetable).length === 0 ? (
          <div className="flex items-center justify-center py-12">
            <div className="text-center">
              <Calendar className="w-8 h-8 mx-auto mb-2 text-neutral-400" />
              <p className="text-neutral-600 mb-4">No timetable available for this program and semester</p>
              <button
                onClick={loadTimetable}
                className="btn btn-primary"
              >
                Generate Timetable
              </button>
            </div>
          </div>
        ) : (
          <div className="overflow-x-auto">
            <table className="w-full border-collapse">
              <thead>
                <tr className="border-b border-neutral-200">
                  <th className="text-left py-3 px-4 font-semibold text-primary-900 bg-neutral-50 min-w-[120px]">
                    Time
                  </th>
                  {days.map((day) => (
                    <th key={day} className="text-left py-3 px-4 font-semibold text-primary-900 bg-neutral-50 min-w-[200px]">
                      {day}
                    </th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {/* Generate time slots dynamically from timetable data */}
                {(() => {
                  const allTimes = new Set()
                  Object.values(timetable).forEach(daySchedule => {
                    Object.keys(daySchedule).forEach(time => allTimes.add(time))
                  })
                  const timeSlots = Array.from(allTimes).sort()
                  
                  return timeSlots.map((slot) => (
                    <tr key={slot} className="border-b border-neutral-100 hover:bg-neutral-50/50">
                      <td className="py-4 px-4 font-medium text-neutral-700 bg-neutral-25">
                        <div className="flex items-center space-x-2">
                          <Clock className="w-4 h-4 text-neutral-400" />
                          <span>{slot}</span>
                        </div>
                      </td>
                      {days.map((day) => {
                        const classInfo = timetable[day]?.[slot]
                        return (
                          <td key={`${day}-${slot}`} className="py-4 px-4">
                            {classInfo ? (
                              <motion.div
                                initial={{ opacity: 0, y: 10 }}
                                animate={{ opacity: 1, y: 0 }}
                                className="bg-gradient-to-br from-blue-50 to-indigo-50 border border-blue-200 rounded-lg p-3 hover:shadow-md transition-shadow cursor-pointer"
                              >
                                <div className="font-semibold text-primary-900 text-sm mb-1 flex items-center">
                                  <BookOpen className="w-3 h-3 mr-1" />
                                  {classInfo.course}
                                </div>
                                {classInfo.code && (
                                  <div className="text-xs text-neutral-500 mb-1">
                                    {classInfo.code} {classInfo.category && `(${classInfo.category})`}
                                  </div>
                                )}
                                <div className="text-xs text-neutral-600 flex items-center mb-1">
                                  <User className="w-3 h-3 mr-1" />
                                  {classInfo.faculty}
                                </div>
                                <div className="text-xs text-neutral-600 flex items-center">
                                  <MapPin className="w-3 h-3 mr-1" />
                                  {classInfo.room}
                                  {classInfo.credits && (
                                    <span className="ml-2 px-1 py-0.5 bg-blue-100 text-blue-700 rounded text-xs">
                                      {classInfo.credits} credits
                                    </span>
                                  )}
                                </div>
                              </motion.div>
                            ) : (
                              <div className="h-16 border-2 border-dashed border-neutral-200 rounded-lg flex items-center justify-center text-neutral-400">
                                <span className="text-xs">Free</span>
                              </div>
                            )}
                          </td>
                        )
                      })}
                    </tr>
                  ))
                })()}
              </tbody>
            </table>
          </div>
        )}
      </div>

      {/* Statistics Section */}
      {Object.keys(timetable).length > 0 && (
        <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
          <div className="card p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-blue-100 rounded-lg">
                <BookOpen className="w-5 h-5 text-blue-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-600">Total Classes</p>
                <p className="text-xl font-semibold text-primary-900">
                  {Object.values(timetable).reduce((total, day) => total + Object.keys(day).length, 0)}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-green-100 rounded-lg">
                <User className="w-5 h-5 text-green-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-600">Unique Faculty</p>
                <p className="text-xl font-semibold text-primary-900">
                  {new Set(
                    Object.values(timetable)
                      .flatMap(day => Object.values(day))
                      .map(slot => slot.faculty)
                  ).size}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-purple-100 rounded-lg">
                <MapPin className="w-5 h-5 text-purple-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-600">Rooms Used</p>
                <p className="text-xl font-semibold text-primary-900">
                  {new Set(
                    Object.values(timetable)
                      .flatMap(day => Object.values(day))
                      .map(slot => slot.room)
                  ).size}
                </p>
              </div>
            </div>
          </div>
          
          <div className="card p-4">
            <div className="flex items-center space-x-3">
              <div className="p-2 bg-orange-100 rounded-lg">
                <Clock className="w-5 h-5 text-orange-600" />
              </div>
              <div>
                <p className="text-sm text-neutral-600">Total Credits</p>
                <p className="text-xl font-semibold text-primary-900">
                  {Object.values(timetable)
                    .flatMap(day => Object.values(day))
                    .reduce((total, slot) => total + (slot.credits || 0), 0)}
                </p>
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}