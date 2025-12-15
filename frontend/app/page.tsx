
"use client";
import React, { useState } from "react";
import axios from "axios";

export default function Home() {
  const [files, setFiles] = useState({
    students: null,
    teachers: null,
    slots: null,
    busy: null,
  });
  const [schedule, setSchedule] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>, key: string) => {
    setFiles({ ...files, [key]: e.target.files?.[0] || null });
  };

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);
    setError("");
    setSchedule([]);
    const formData = new FormData();
    formData.append("students", files.students);
    formData.append("teachers", files.teachers);
    formData.append("slots", files.slots);
    formData.append("busy", files.busy);
    try {
      const res = await axios.post("http://localhost:8000/generate-schedule", formData, {
        headers: { "Content-Type": "multipart/form-data" },
      });
      setSchedule(res.data);
    } catch (err) {
      setError("Failed to generate schedule. Please check your files and try again.");
    }
    setLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900 flex items-center justify-center p-6">
      <div className="bg-white/10 backdrop-blur-md rounded-2xl shadow-2xl flex flex-col md:flex-row w-full max-w-5xl overflow-hidden border border-gray-700">
        {/* Left Panel: File Uploads */}
        <form
          className="md:w-1/3 w-full p-10 flex flex-col gap-7 bg-gradient-to-b from-gray-900/80 to-gray-800/80"
          onSubmit={handleSubmit}
        >
          <h2 className="text-3xl font-extrabold mb-2 text-white tracking-tight text-center drop-shadow">Upload CSV Files</h2>
          <div className="space-y-4">
            <div>
              <label className="block font-semibold mb-1 text-gray-200">Students</label>
              <input type="file" accept=".csv" required onChange={e => handleFileChange(e, "students")} className="block w-full text-sm text-gray-200 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 transition" />
            </div>
            <div>
              <label className="block font-semibold mb-1 text-gray-200">Teachers</label>
              <input type="file" accept=".csv" required onChange={e => handleFileChange(e, "teachers")} className="block w-full text-sm text-gray-200 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 transition" />
            </div>
            <div>
              <label className="block font-semibold mb-1 text-gray-200">Slots</label>
              <input type="file" accept=".csv" required onChange={e => handleFileChange(e, "slots")} className="block w-full text-sm text-gray-200 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 transition" />
            </div>
            <div>
              <label className="block font-semibold mb-1 text-gray-200">Busy</label>
              <input type="file" accept=".csv" required onChange={e => handleFileChange(e, "busy")} className="block w-full text-sm text-gray-200 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 transition" />
            </div>
          </div>
          <button
            type="submit"
            className="mt-8 bg-gradient-to-r from-blue-600 to-blue-500 text-white py-2 rounded-lg font-bold shadow-lg hover:from-blue-700 hover:to-blue-600 transition text-lg tracking-wide"
            disabled={loading}
          >
            {loading ? (
              <span className="flex items-center justify-center gap-2"><svg className="animate-spin h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24"><circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle><path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8v8z"></path></svg>Generating...</span>
            ) : "Generate Schedule"}
          </button>
          {error && <div className="text-red-400 mt-2 text-center font-semibold">{error}</div>}
        </form>
        {/* Right Panel: Schedule Table */}
        <div className="md:w-2/3 w-full p-10 overflow-x-auto flex flex-col items-center justify-center bg-white/5">
          <h2 className="text-3xl font-extrabold mb-4 text-white tracking-tight text-center drop-shadow">Remedial Class Schedule</h2>
          {schedule.length === 0 ? (
            <div className="text-gray-300 text-lg mt-8">No schedule generated yet.</div>
          ) : (
            <div className="w-full max-w-2xl">
              <table className="min-w-full border border-gray-700 rounded-xl overflow-hidden shadow-lg bg-white/90">
                <thead className="bg-blue-600/90">
                  <tr>
                    <th className="px-6 py-3 text-left text-white font-bold">Student Name</th>
                    <th className="px-6 py-3 text-left text-white font-bold">Subject</th>
                    <th className="px-6 py-3 text-left text-white font-bold">Teacher Name</th>
                    <th className="px-6 py-3 text-left text-white font-bold">Slot ID</th>
                  </tr>
                </thead>
                <tbody>
                  {schedule.map((row: any, idx: number) => (
                    <tr key={idx} className="border-t border-gray-200 hover:bg-blue-50/80 transition">
                      <td className="px-6 py-3 font-medium text-gray-900">{row["Student Name"]}</td>
                      <td className="px-6 py-3 text-gray-800">{row["Subject"]}</td>
                      <td className="px-6 py-3 text-gray-800">{row["Teacher Name"]}</td>
                      <td className="px-6 py-3 text-gray-800">{row["Slot_ID"]}</td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
