import { Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import Dashboard from './pages/Dashboard'
import TimetableGenerator from './pages/TimetableGenerator'
import { Programs, Faculty, Courses, Rooms, Students, ViewTimetable, Settings } from './pages'

function App() {
  return (
    <Routes>
      <Route path="/" element={<Layout />}>
        <Route index element={<Navigate to="/dashboard" replace />} />
        <Route path="dashboard" element={<Dashboard />} />
        <Route path="generate" element={<TimetableGenerator />} />
        <Route path="timetable" element={<ViewTimetable />} />
        <Route path="programs" element={<Programs />} />
        <Route path="faculty" element={<Faculty />} />
        <Route path="courses" element={<Courses />} />
        <Route path="rooms" element={<Rooms />} />
        <Route path="students" element={<Students />} />
        <Route path="settings" element={<Settings />} />
      </Route>
    </Routes>
  )
}

export default App
