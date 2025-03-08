import React, { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { Card } from "@/components/ui/card";
import { BarChart, Bar, XAxis, YAxis, Tooltip, Legend, ResponsiveContainer } from "recharts";
import { Button } from "@/components/ui/button";
import { Moon, Sun, RefreshCcw, Play, StopCircle, Folder } from "lucide-react";

export default function LogDashboard() {
  const [logs, setLogs] = useState([]);
  const [darkMode, setDarkMode] = useState(true);
  const [loading, setLoading] = useState(false);
  const [isMonitoring, setIsMonitoring] = useState(false);
  const [directoryPath, setDirectoryPath] = useState("");
  const [isValidDirectory, setIsValidDirectory] = useState(false); // Track if directory is valid
  const [selectedDirectory, setSelectedDirectory] = useState(""); // Track the selected directory

  useEffect(() => {
    document.documentElement.classList.toggle("dark", darkMode);
  }, [darkMode]);

  const fetchLogs = () => {
    setLoading(true);
    fetch("http://localhost:5000/logs")
      .then((response) => response.json())
      .then((data) => {
        setLogs(data);
        setLoading(false);
      })
      .catch((error) => {
        console.error("Error fetching logs:", error);
        setLoading(false);
      });
  };

  // Validate directory
  const validateDirectory = async (dirPath) => {
    try {
      const response = await fetch("http://localhost:5000/validate_directory", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ directory: dirPath }),
      });
      const data = await response.json();
      if (data.status === "valid") {
        setIsValidDirectory(true);
      } else {
        setIsValidDirectory(false);
        alert("Invalid directory. Please enter a valid path.");
      }
    } catch (error) {
      console.error("Directory validation failed:", error);
    }
  };

  const handleDirectoryChange = (e) => {
    setDirectoryPath(e.target.value);
    validateDirectory(e.target.value); // Validate directory on change
  };

  const toggleMonitoring = async () => {
    if (!isValidDirectory) {
      alert("Please provide a valid directory before starting monitoring.");
      return;
    }

    const url = isMonitoring ? "http://localhost:5000/stop" : "http://localhost:5000/start";

    try {
      const response = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ directory: directoryPath }),
      });

      const data = await response.json();
      if (!response.ok) {
        console.error("Error toggling monitoring:", data);
        alert(`Error: ${data.status || "Unknown error"}`);
        return;
      }

      setIsMonitoring(!isMonitoring);
      alert(data.status);
    } catch (error) {
      console.error("Request failed:", error);
      alert("Failed to connect to the server.");
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  const logCounts = logs.reduce((acc, log) => {
    const type = log.message.includes("ADDED")
      ? "Added"
      : log.message.includes("MODIFIED")
        ? "Modified"
        : log.message.includes("DELETED")
          ? "Deleted"
          : log.message.includes("RENAMED")
            ? "Renamed"
            : "Other";
    acc[type] = (acc[type] || 0) + 1;
    return acc;
  }, {});

  const clearLogs = async () => {
    try {
      const response = await fetch("http://localhost:5000/clear_logs", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
      });

      if (!response.ok) {
        const errorData = await response.json();
        console.error("Error clearing logs:", errorData);
        alert(`Error: ${errorData.status || "Unknown error"}`);
        return;
      }

      alert("Logs cleared successfully!");
      setLogs([]); // Clear logs in UI
    } catch (error) {
      console.error("Request failed:", error);
      alert("Failed to connect to the server.");
    }
  };

  const chartData = Object.entries(logCounts).map(([name, value]) => ({
    name,
    value,
  }));

  return (
    <div className={`w-full min-h-screen ${darkMode ? "bg-gray-900 text-white" : "bg-white text-gray-900"} transition-all`}>
      <div className="flex justify-between items-center p-6">
        <h1 className="text-2xl font-bold">📊 File Monitor Dashboard</h1>
        <div className="flex gap-4">
          {/* Refresh Button */}
          <Button onClick={fetchLogs} disabled={loading} className="relative overflow-hidden">
            <motion.div
              initial={{ scale: 1 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              {loading ? (
                <motion.div animate={{ rotate: 360 }} transition={{ repeat: Infinity, duration: 1, ease: "linear" }}>
                  <RefreshCcw className="w-5 h-5 animate-spin" />
                </motion.div>
              ) : (
                <RefreshCcw className="w-5 h-5" />
              )}
            </motion.div>
          </Button>

          {/* Input for Directory */}
          <input
            type="text"
            value={directoryPath}
            onChange={handleDirectoryChange}
            className={`p-2 rounded border ${darkMode ? "border-gray-700 bg-gray-800 text-white" : "border-gray-300 bg-white shadow-sm"}`}
            placeholder="Enter directory path"
          />

          {/* Start/Stop Monitoring Button */}
          <Button onClick={toggleMonitoring} className="relative overflow-hidden">
            <motion.div
              initial={{ scale: 1 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              {isMonitoring ? <StopCircle className="w-5 h-5 text-red-500" /> : <Play className="w-5 h-5 text-green-500" />}
            </motion.div>
          </Button>

          {/* Clear Logs Button */}
          <Button onClick={clearLogs} className="relative overflow-hidden">
            <motion.div
              initial={{ scale: 1 }}
              whileTap={{ scale: 0.9 }}
              transition={{ type: "spring", stiffness: 400, damping: 10 }}
            >
              🗑️ Clear Logs
            </motion.div>
          </Button>

          {/* Dark Mode Toggle */}
          <Button onClick={() => setDarkMode(!darkMode)}>
            {darkMode ? <Sun className="w-5 h-5" /> : <Moon className="w-5 h-5" />}
          </Button>
        </div>
      </div>

      {/* Display Selected Directory */}
      <div className="px-6">
        <p className={`text-lg font-medium p-2 rounded-md ${darkMode ? "bg-gray-800 border border-gray-700" : "bg-gray-100 border border-gray-300 shadow-sm"}`}>
          📂 Monitoring Directory: {selectedDirectory || "Not selected"}
        </p>
      </div>

      {/* Animated Insights Cards */}
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-6 p-6">
        {Object.entries(logCounts).map(([type, count]) => (
          <motion.div key={type} initial={{ opacity: 0, scale: 0.8 }} animate={{ opacity: 1, scale: 1 }} transition={{ duration: 0.5 }}>
            <Card className={`p-4 shadow-lg rounded-2xl ${darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-300 shadow-md"}`}>
              <h2 className="text-lg font-semibold">{type}</h2>
              <p className="text-3xl font-bold">{count}</p>
            </Card>
          </motion.div>
        ))}
      </div>

      {/* Log Data Visualization */}
      <div className="p-6">
        <Card className={`shadow-lg rounded-2xl p-4 border ${darkMode ? "bg-gray-800 border-gray-700" : "bg-white border-gray-300 shadow-md"}`}>
          <h2 className="text-xl font-semibold">📈 Log Activity Overview</h2>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={Object.entries(logCounts).map(([name, value]) => ({ name, value }))}>
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip
                contentStyle={{
                  backgroundColor: darkMode ? "#1F2937" : "#ffffff",
                  color: darkMode ? "#F9FAFB" : "#000000",
                }}
              />
              <Legend />
              <Bar dataKey="value" fill={darkMode ? "#60A5FA" : "#3B82F6"} />
            </BarChart>
          </ResponsiveContainer>
        </Card>
      </div>

      {/* Log List with Scrolling */}
      <div className="p-6">
        <Card className="shadow-lg rounded-2xl p-4">
          <h2 className="text-xl font-semibold">📜 Recent Logs</h2>
          <div className={`mt-4 max-h-96 overflow-y-auto rounded-lg p-2 border ${darkMode ? "border-gray-700" : "border-gray-300 shadow-md"}`}>
            {logs.length > 0 ? (
              logs
                .slice()
                .reverse()
                .map((log, index) => {
                  let logColor = "text-gray-500";
                  if (log.message.includes("ADDED")) logColor = "text-green-500";
                  else if (log.message.includes("MODIFIED")) logColor = "text-yellow-500";
                  else if (log.message.includes("DELETED")) logColor = "text-red-500";
                  else if (log.message.includes("RENAMED")) logColor = "text-blue-500";

                  return (
                    <motion.div
                      key={index}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.05 }}
                      className={`border-b py-2 ${darkMode ? "border-gray-700" : "border-gray-300"}`}
                    >
                      <p className="text-sm text-gray-400">{log.timestamp}</p>
                      <p className={`text-md font-medium ${logColor}`}>{log.message}</p>
                    </motion.div>
                  );
                })
            ) : (
              <p className="text-gray-500 text-center">No logs found.</p>
            )}
          </div>
        </Card>
      </div>
    </div>
  );
}
