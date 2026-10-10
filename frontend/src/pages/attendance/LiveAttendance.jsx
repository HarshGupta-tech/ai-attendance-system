import React, { useState, useEffect, useRef } from 'react';
import { Camera, VideoOff, Users, Clock, AlertTriangle } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card, Badge } from '../../components/common';
import toast from 'react-hot-toast';

export default function LiveAttendance() {
  const [sessions, setSessions] = useState([]);
  const [activeSession, setActiveSession] = useState('');
  const [isCameraOn, setIsCameraOn] = useState(false);
  const [recognizedStudents, setRecognizedStudents] = useState([]);
  const [stats, setStats] = useState({ totalRecognized: 0, totalStudents: 0, unknownFaces: 0 });
  const [frameCount, setFrameCount] = useState(0);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const recognitionIntervalRef = useRef(null);

  useEffect(() => {
    // Fetch active sessions
    api.get('/attendance/sessions?status=active').then(res => {
      const active = res.data.items || res.data || [];
      setSessions(active);
      if (active.length > 0) setActiveSession(active[0].id);
    });

    return () => stopCamera();
  }, []);

  const startCamera = async () => {
    if (!activeSession) {
      toast.error('Please select an active session first');
      return;
    }
    
    try {
      // First try high resolution, fallback to any available resolution if that fails
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({ video: { width: { ideal: 1280 }, height: { ideal: 720 } } });
      } catch (err) {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
      }
      
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setIsCameraOn(true);
        startRecognitionLoop();
      }
    } catch (err) {
      console.error(err);
      toast.error('Could not access camera. Ensure you are on localhost or HTTPS, and permissions are granted.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
    }
    setIsCameraOn(false);
    if (recognitionIntervalRef.current) {
      clearInterval(recognitionIntervalRef.current);
    }
  };

  const startRecognitionLoop = () => {
    // Process a frame every 2 seconds
    recognitionIntervalRef.current = setInterval(processFrame, 2000);
  };

  const processFrame = async () => {
    if (!videoRef.current || !canvasRef.current || !activeSession) return;
    
    const video = videoRef.current;
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    const base64Image = canvas.toDataURL('image/jpeg', 0.8);
    
    setFrameCount(prev => prev + 1);
    
    try {
      const res = await api.post('/attendance/recognize', {
        sessionId: activeSession,
        imageData: base64Image
      });
      
      const { recognized = [], unknownCount = 0, boundingBoxes = [] } = res.data;
      
      // Update UI with recognized students
      if (recognized.length > 0) {
        setRecognizedStudents(prev => {
          const newStudents = [...prev];
          recognized.forEach(student => {
            if (!newStudents.find(s => s.studentId === student.studentId)) {
              newStudents.unshift({ ...student, time: new Date().toLocaleTimeString() });
              // Play a subtle sound if possible
            }
          });
          return newStudents;
        });
        
        setStats(prev => ({
          ...prev,
          totalRecognized: prev.totalRecognized + recognized.length,
          unknownFaces: unknownCount
        }));
      }
      
      // Optional: Draw bounding boxes on another canvas overlay
    } catch (err) {
      console.error('Recognition error', err);
    }
  };

  const currentSessionData = sessions.find(s => s.id === activeSession);

  return (
    <div className="h-[calc(100vh-100px)] flex flex-col space-y-4">
      {/* Top Bar */}
      <Card className="flex items-center justify-between p-4 flex-shrink-0">
        <div className="flex items-center gap-4">
          <h1 className="text-xl font-bold flex items-center gap-2">
            <span className="w-3 h-3 rounded-full bg-red-500 animate-pulse"></span>
            Live Attendance
          </h1>
          <select 
            value={activeSession} 
            onChange={(e) => setActiveSession(e.target.value)}
            className="p-2 border rounded-md bg-white min-w-[250px]"
            disabled={isCameraOn}
          >
            <option value="">Select Active Session</option>
            {sessions.map(s => <option key={s.id} value={s.id}>{s.subjectName} ({s.course} S{s.semester})</option>)}
          </select>
          {currentSessionData?.session_code && (
            <div className="ml-4 flex items-center gap-2 px-4 py-1.5 bg-teal-50 border border-teal-200 rounded-lg text-teal-800">
              <span className="text-xs font-semibold uppercase tracking-wider">Session Code:</span>
              <span className="text-lg font-mono font-bold tracking-[0.2em]">{currentSessionData.session_code}</span>
            </div>
          )}
        </div>
        
        <div className="flex gap-2">
          {!isCameraOn ? (
            <Button onClick={startCamera} className="bg-green-600 text-white flex items-center gap-2">
              <Camera size={16} /> Start Camera
            </Button>
          ) : (
            <Button onClick={stopCamera} variant="danger" className="bg-red-600 text-white flex items-center gap-2">
              <VideoOff size={16} /> Stop Camera
            </Button>
          )}
        </div>
      </Card>

      {/* Main Content Split */}
      <div className="flex flex-col lg:flex-row gap-4 flex-1 min-h-0">
        {/* Left: Video Feed */}
        <div className="w-full lg:w-3/5 bg-black rounded-lg border-2 border-gray-800 flex flex-col relative overflow-hidden">
          <video 
            ref={videoRef} 
            autoPlay 
            playsInline 
            muted 
            className={`w-full h-full object-cover ${!isCameraOn ? 'hidden' : ''}`} 
          />
          <canvas ref={canvasRef} className="hidden" />
          
          {isCameraOn ? (
            <div className="absolute top-4 right-4 bg-black/60 text-white px-3 py-1 rounded-full text-xs font-mono flex items-center gap-2">
              <span className="w-2 h-2 rounded-full bg-green-500"></span> Live Processing (Frame: {frameCount})
            </div>
          ) : (
            <div className="flex-1 flex flex-col items-center justify-center text-gray-500 min-h-[360px]">
              <Camera size={48} className="mb-4 opacity-50" />
              <p>Camera is currently off</p>
              <p className="text-sm">Select a session and click Start Camera</p>
            </div>
          )}
        </div>

        {/* Right: Info & Recognition List */}
        <div className="w-full lg:w-2/5 flex flex-col gap-4">
          <Card className="flex-shrink-0">
            <h2 className="text-lg font-semibold mb-2 flex items-center gap-2"><Clock size={18} /> Session Info</h2>
            {currentSessionData ? (
              <div className="space-y-1 text-sm">
                <p><strong>Subject:</strong> {currentSessionData.subjectName}</p>
                <p><strong>Class:</strong> {currentSessionData.course} Sem-{currentSessionData.semester} Sec-{currentSessionData.section}</p>
                <p><strong>Time:</strong> {currentSessionData.startTime} - {currentSessionData.endTime}</p>
              </div>
            ) : (
              <p className="text-sm text-gray-500">No session selected.</p>
            )}
          </Card>

          <Card className="flex-shrink-0">
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-indigo-50 p-3 rounded-lg text-center">
                <p className="text-xs text-indigo-600 font-semibold">Recognized</p>
                <p className="text-2xl font-bold text-indigo-700">{stats.totalRecognized}</p>
              </div>
              <div className="bg-red-50 p-3 rounded-lg text-center">
                <p className="text-xs text-red-600 font-semibold">Unknown Faces</p>
                <p className="text-2xl font-bold text-red-700">{stats.unknownFaces}</p>
              </div>
            </div>
          </Card>

          <Card className="flex-1 flex flex-col min-h-0">
            <h2 className="text-lg font-semibold mb-2 flex items-center gap-2 border-b pb-2"><Users size={18} /> Recently Recognized</h2>
            <div className="flex-1 overflow-y-auto space-y-2 pr-2 custom-scrollbar">
              {recognizedStudents.length > 0 ? (
                recognizedStudents.map((student, idx) => (
                  <div key={idx} className="flex items-center justify-between p-3 bg-gray-50 border rounded-lg animate-in fade-in slide-in-from-right-4">
                    <div className="flex flex-col">
                      <span className="font-medium text-gray-900">{student.name}</span>
                      <span className="text-xs text-gray-500">{student.studentId} • {student.time}</span>
                    </div>
                    <Badge color={student.status === 'late' ? 'yellow' : 'green'}>
                      {student.status.toUpperCase()}
                    </Badge>
                  </div>
                ))
              ) : (
                <div className="h-full flex flex-col items-center justify-center text-gray-400">
                  <Users size={32} className="mb-2 opacity-50" />
                  <p className="text-sm">No faces recognized yet</p>
                </div>
              )}
            </div>
          </Card>
        </div>
      </div>
    </div>
  );
}
