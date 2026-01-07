import React, { useState } from 'react';
import { User, FileText, Send, Settings, Trash2, Download } from 'lucide-react';

const App = () => {
  const [files, setFiles] = useState([]);
  const [candidates, setCandidates] = useState([]);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    if (e.target.files) {
      setFiles(Array.from(e.target.files));
    }
  };

  const handleUpload = async () => {
    if (files.length === 0) return;
    setIsLoading(true);
    const formData = new FormData();
    files.forEach(file => formData.append("files", file));

    try {
      const response = await fetch('http://127.0.0.1:8000/upload', {
        method: 'POST',
        body: formData,
      });
      const result = await response.json();
      if (result.status === 'success') setCandidates(result.data);
    } catch (error) {
      alert("Failed to connect to backend.");
    } finally {
      setIsLoading(false);
    }
  };

  // --- NEW: DOWNLOAD AS CSV ---
  const downloadCSV = () => {
    if (candidates.length === 0) {
      alert("No data to download!");
      return;
    }

    // Define CSV headers
    const headers = [
      "ID", "Name", "Role", "Email", "Phone", "Manager", "Location", "DOJ",
      "Experience (Years)", "Education", "CGPA", "Bank", "Account", "Aadhar", "T-Shirt", "Status"
    ];

    // Map data to CSV rows
    const rows = candidates.map(c => [
      c.candidate_id || "",
      c.full_name || "",
      c.role || "",
      c.email || "",
      c.phone_number ? `'${c.phone_number}` : "",  // Force Text
      c.reporting_manager || "",
      c.location || "",
      c.date_of_joining || "",
      c.experience_years || "",
      c.education || "",
      c.cgpa || "",
      c.bank_name || "",
      c.account_number ? `${c.account_number}` : "", // Force Text (Fixes 5.01E+13)
      c.aadhar_number ? `${c.aadhar_number}` : "",   // Force Text (Fixes Scientific Notation)
      c.t_shirt_size || "",
      (!c.bank_name || !c.aadhar_number) ? "Missing Docs" : "Ready"
    ]);

    // Create CSV string
    const csvContent = [
      headers.join(","),
      ...rows.map(row => row.map(cell => `"${cell}"`).join(","))
    ].join("\n");

    // Create a download link
    const blob = new Blob([csvContent], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const link = document.createElement('a');
    link.href = url;
    link.download = `HR_Dashboard_Export_${new Date().toISOString().split('T')[0]}.csv`;
    link.click();
    window.URL.revokeObjectURL(url);
  };

  return (
    <div className="min-h-screen bg-[#050810] text-gray-300 font-sans selection:bg-blue-500 selection:text-white">
      <nav className="flex items-center justify-between px-8 py-5 bg-[#0b0f1a] border-b border-gray-800">
        <div>
          <h1 className="text-2xl font-bold tracking-tight text-white">
            <span className="text-blue-500">HR INFORMATION</span> DASHBOARD
          </h1>
          <p className="text-xs text-gray-500 uppercase tracking-wider mt-0.5">Automated Email & Reminder Console</p>
        </div>
        <div className="flex space-x-1 bg-[#111827] p-1 rounded-full border border-gray-800">
          <NavButton active text="Recipients" icon={<User size={14} />} />
          <NavButton text="Templates" icon={<FileText size={14} />} />
          <NavButton text="Send / Schedule" icon={<Send size={14} />} />
          <NavButton text="Actions" icon={<Settings size={14} />} />
        </div>
      </nav>

      <main className="max-w-[98%] mx-auto mt-10 p-6">
        <div className="bg-[#111827] border border-gray-800 rounded-xl shadow-2xl overflow-hidden">
          <div className="p-6 border-b border-gray-800 flex justify-between items-center">
            <div className="flex items-center gap-3">
              <User className="text-white" />
              <h2 className="text-xl font-semibold text-white">Recipients</h2>
              <span className="bg-[#1f2937] text-xs font-bold px-2 py-0.5 rounded text-gray-400 border border-gray-700">PEOPLE</span>
            </div>
          </div>

          <div className="p-8 space-y-8">
            <div className="bg-[#0b0f1a] p-6 rounded-xl border border-dashed border-gray-700 text-center">
              <div className="flex flex-col items-center gap-4">
                <div className="p-4 bg-[#1f2937] rounded-full text-blue-400">
                  <FileText size={32} />
                </div>
                <div>
                  <h3 className="text-lg font-medium text-white">Upload Candidate Documents</h3>
                  <p className="text-sm text-gray-500 mt-1">Select Offer Letters, Resumes, KYC Forms (PDF)</p>
                </div>
                <div className="flex items-center gap-4 mt-2">
                  <input type="file" multiple accept=".pdf" onChange={handleFileChange} className="hidden" id="file-upload" />
                  <label htmlFor="file-upload" className="cursor-pointer px-6 py-2.5 bg-[#1f2937] border border-gray-600 hover:bg-gray-700 text-white rounded-lg text-sm font-medium transition-all">
                    {files.length > 0 ? `${files.length} Files Selected` : "Choose PDF Files"}
                  </label>
                  <button onClick={handleUpload} disabled={isLoading || files.length === 0} className={`px-6 py-2.5 rounded-lg text-sm font-medium transition-all ${isLoading ? "bg-gray-700 text-gray-400 cursor-not-allowed" : "bg-blue-600 hover:bg-blue-700 text-white shadow-lg shadow-blue-900/50"}`}>
                    {isLoading ? "Extracting Data..." : "Upload & Process"}
                  </button>
                </div>
              </div>
            </div>

            {/* --- NEW: Download CSV Button --- */}
            {candidates.length > 0 && (
              <div className="flex justify-end">
                <button 
                  onClick={downloadCSV}
                  className="flex items-center gap-2 px-6 py-2.5 bg-green-600 hover:bg-green-700 text-white rounded-lg text-sm font-medium transition-all shadow-lg shadow-green-900/50"
                >
                  <Download size={16} />
                  Download as CSV
                </button>
              </div>
            )}

            <div className="rounded-lg border border-gray-800 overflow-hidden bg-[#0b0f1a]">
              <div className="overflow-x-auto">
                <table className="w-full text-left text-sm whitespace-nowrap">
                  <thead>
                    <tr className="bg-[#1f2937] text-gray-400 border-b border-gray-800">
                      <th className="px-6 py-3 font-medium">ID</th>
                      <th className="px-6 py-3 font-medium">NAME</th>
                      <th className="px-6 py-3 font-medium">ROLE</th>
                      <th className="px-6 py-3 font-medium">EMAIL</th>
                      <th className="px-6 py-3 font-medium">PHONE</th>
                      <th className="px-6 py-3 font-medium">MANAGER</th>
                      <th className="px-6 py-3 font-medium">LOCATION</th>
                      <th className="px-6 py-3 font-medium">DOJ</th>
                      <th className="px-6 py-3 font-medium">EXP (YRS)</th>
                      <th className="px-6 py-3 font-medium">EDUCATION</th>
                      <th className="px-6 py-3 font-medium">CGPA</th>
                      <th className="px-6 py-3 font-medium">BANK</th>
                      <th className="px-6 py-3 font-medium">ACCOUNT</th>
                      <th className="px-6 py-3 font-medium">AADHAR</th>
                      <th className="px-6 py-3 font-medium">T-SHIRT</th>
                      <th className="px-6 py-3 font-medium">STATUS</th>
                      <th className="px-6 py-3 text-right">ACTION</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-800">
                    {candidates.length === 0 ? (
                      <tr>
                        <td colSpan="17" className="px-6 py-12 text-center text-gray-600">No data yet. Upload PDFs above.</td>
                      </tr>
                    ) : (
                      candidates.map((c, idx) => (
                        <tr key={idx} className="hover:bg-[#111827] transition-colors">
                          <td className="px-6 py-4 text-gray-500">#{c.candidate_id}</td>
                          <td className="px-6 py-4 font-medium text-white">{c.full_name}</td>
                          <td className="px-6 py-4"><span className="bg-blue-900/30 text-blue-400 px-2 py-1 rounded text-xs border border-blue-900/50">{c.role}</span></td>
                          <td className="px-6 py-4 text-gray-400">{c.email}</td>
                          <td className="px-6 py-4 text-gray-400">{c.phone_number || "-"}</td>
                          <td className="px-6 py-4 text-gray-400">{c.reporting_manager || "-"}</td>
                          <td className="px-6 py-4 text-gray-400">{c.location}</td>
                          <td className="px-6 py-4 text-gray-400">{c.date_of_joining}</td>
                          <td className="px-6 py-4 text-center text-gray-300">{c.experience_years || "-"}</td>
                          <td className="px-6 py-4 text-gray-400">{c.education || "-"}</td>
                          <td className="px-6 py-4 text-center text-gray-300">{c.cgpa || "-"}</td>
                          <td className="px-6 py-4 text-gray-400">{c.bank_name || "-"}</td>
                          <td className="px-6 py-4"><MaskedCell value={c.account_number} type="account" /></td>
                          <td className="px-6 py-4"><MaskedCell value={c.aadhar_number} type="aadhar" /></td>
                          <td className="px-6 py-4 text-center text-gray-400">{c.t_shirt_size || "-"}</td>
                          <td className="px-6 py-4">
                            {(!c.bank_name || !c.aadhar_number) ? <span className="text-red-400 text-xs bg-red-900/20 px-2 py-1 rounded border border-red-900/50">Missing Docs</span> : <span className="text-green-400 text-xs bg-green-900/20 px-2 py-1 rounded border border-green-900/50">Ready</span>}
                          </td>
                          <td className="px-6 py-4 text-right"><button className="text-gray-600 hover:text-red-400 transition-colors"><Trash2 size={16} /></button></td>
                        </tr>
                      ))
                    )}
                  </tbody>
                </table>
              </div>
            </div>
          </div>
        </div>
      </main>
    </div>
  );
};

const MaskedCell = ({ value, type }) => {
  if (!value) return <span className="text-gray-600 font-mono">-</span>;
  const len = value.length;
  const visiblePart = value.slice(-4);
  const displayMask = `**** ${visiblePart}`; 

  return (
    <div className="group relative cursor-pointer font-mono text-gray-400">
      <span className="group-hover:hidden transition-all duration-200">{displayMask}</span>
      <span className="hidden group-hover:inline text-blue-400 bg-blue-900/20 px-1 rounded transition-all duration-200 select-all">{value}</span>
    </div>
  );
};

const NavButton = ({ text, active, icon }) => (
  <button className={`flex items-center gap-2 px-4 py-2 rounded-full text-sm font-medium transition-all ${active ? "bg-blue-600 text-white shadow-lg shadow-blue-900/50" : "text-gray-400 hover:text-white hover:bg-gray-800"}`}>
    {icon} {text}
  </button>
);

export default App;
