import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { Camera, ShieldCheck, KeyRound, CheckCircle2, XCircle, Loader2 } from 'lucide-react';
import api from '../../utils/api';
import { Card, Button } from '../../components/common';
import toast from 'react-hot-toast';

export default function MarkAttendance() {
  const navigate = useNavigate();

  const [step, setStep] = useState(1); // 1 = enter code, 2 = face scan, 3 = result
  const [sessionCode, setSessionCode] = useState('');
  const [streamActive, setStreamActive] = useState(false);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [result, setResult] = useState(null); // {success, message}

  const videoRef = useRef(null);
  const canvasRef = useRef(null);

  useEffect(() => {
    return () => stopCamera();
  }, []);

  const startCamera = async () => {
    try {
      let stream;
      try {
        stream = await navigator.mediaDevices.getUserMedia({
          video: { width: { ideal: 640 }, height: { ideal: 480 }, facingMode: 'user' }
        });
      } catch (err) {
        stream = await navigator.mediaDevices.getUserMedia({ video: true });
      }

      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setStreamActive(true);
      }
    } catch (err) {
      console.error(err);
      toast.error('Unable to access camera. Ensure you are on localhost or HTTPS, and check permissions.');
    }
  };

  const stopCamera = () => {
    if (videoRef.current && videoRef.current.srcObject) {
      videoRef.current.srcObject.getTracks().forEach(track => track.stop());
      setStreamActive(false);
    }
  };

  const handleCodeSubmit = (e) => {
    e.preventDefault();
    if (sessionCode.length !== 6) {
      toast.error('Please enter a valid 6-digit session code');
      return;
    }
    setStep(2);
    // Small delay so the DOM renders the video element before we access it
    setTimeout(() => startCamera(), 100);
  };

  const handleCapture = async () => {
    if (!videoRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);

    const base64Image = canvas.toDataURL('image/jpeg', 0.8);

    setIsSubmitting(true);
    try {
      const res = await api.post('/attendance/self-mark', {
        session_code: sessionCode,
        image_data: base64Image
      });

      stopCamera();
      setResult({ success: true, message: res.data.message, confidence: res.data.confidence });
      setStep(3);
      toast.success('Attendance marked successfully!');
    } catch (err) {
      const detail = err.response?.data?.detail || 'Failed to mark attendance';
      toast.error(detail);
      setResult({ success: false, message: detail });
      setStep(3);
      stopCamera();
    } finally {
      setIsSubmitting(false);
    }
  };

  return (
    <div className="max-w-xl mx-auto space-y-6">
      <div className="text-center">
        <h1 className="text-2xl font-bold text-gray-900 flex items-center justify-center gap-2">
          <ShieldCheck className="text-teal-600" size={28} />
          Mark My Attendance
        </h1>
        <p className="text-gray-500 mt-1 text-sm">Verified attendance with face scan &amp; session code</p>
      </div>

      {/* Step Indicator */}
      <div className="flex justify-center items-center gap-2 text-sm font-medium">
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full ${step >= 1 ? 'bg-teal-100 text-teal-700' : 'bg-gray-100 text-gray-400'}`}>
          <KeyRound size={14} /> 1. Enter Code
        </div>
        <div className="w-6 h-px bg-gray-300" />
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full ${step >= 2 ? 'bg-teal-100 text-teal-700' : 'bg-gray-100 text-gray-400'}`}>
          <Camera size={14} /> 2. Face Scan
        </div>
        <div className="w-6 h-px bg-gray-300" />
        <div className={`flex items-center gap-1.5 px-3 py-1.5 rounded-full ${step >= 3 ? (result?.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700') : 'bg-gray-100 text-gray-400'}`}>
          <CheckCircle2 size={14} /> 3. Result
        </div>
      </div>

      {/* Step 1: Enter Session Code */}
      {step === 1 && (
        <Card className="text-center">
          <div className="flex justify-center mb-6">
            <div className="h-20 w-20 rounded-full bg-teal-50 flex items-center justify-center">
              <KeyRound className="h-10 w-10 text-teal-600" />
            </div>
          </div>
          <h2 className="text-xl font-semibold text-gray-800 mb-2">Enter Session Code</h2>
          <p className="text-gray-500 text-sm mb-6">
            Ask your teacher for the 6-digit session code displayed on their screen.
          </p>
          <form onSubmit={handleCodeSubmit}>
            <input
              type="text"
              value={sessionCode}
              onChange={(e) => setSessionCode(e.target.value.replace(/\D/g, '').slice(0, 6))}
              placeholder="• • • • • •"
              maxLength={6}
              className="w-48 text-center text-3xl font-mono tracking-[0.5em] p-4 border-2 border-gray-300 rounded-xl focus:border-teal-500 focus:ring-2 focus:ring-teal-200 outline-none mx-auto block"
            />
            <Button
              type="submit"
              size="lg"
              className="mt-6 bg-teal-600 hover:bg-teal-700 focus:ring-teal-500"
              disabled={sessionCode.length !== 6}
            >
              Verify Code & Continue
            </Button>
          </form>
        </Card>
      )}

      {/* Step 2: Face Scan */}
      {step === 2 && (
        <Card>
          <h2 className="text-lg font-semibold text-gray-800 mb-4 text-center">Scan Your Face</h2>
          <p className="text-gray-500 text-sm mb-4 text-center">
            Position your face in the camera and click "Verify & Mark Attendance"
          </p>
          <div className="relative bg-black rounded-xl overflow-hidden min-h-[360px] flex items-center justify-center">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="w-full h-full object-cover"
              style={{ transform: 'scaleX(-1)' }}
            />
            <canvas ref={canvasRef} className="hidden" />

            {/* Face guide overlay */}
            <div className="absolute inset-0 flex items-center justify-center pointer-events-none">
              <div className="w-48 h-64 border-4 border-dashed border-white/40 rounded-[50%]" />
            </div>

            {isSubmitting && (
              <div className="absolute inset-0 bg-black/60 flex items-center justify-center">
                <div className="text-center text-white">
                  <Loader2 className="h-12 w-12 animate-spin mx-auto mb-3" />
                  <p className="font-medium">Verifying your face...</p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 flex justify-between items-center">
            <Button variant="outline" onClick={() => { stopCamera(); setStep(1); }}>
              Back
            </Button>
            <Button
              onClick={handleCapture}
              disabled={!streamActive || isSubmitting}
              className="bg-teal-600 hover:bg-teal-700 focus:ring-teal-500 flex items-center gap-2"
            >
              <Camera size={16} /> Verify & Mark Attendance
            </Button>
          </div>
        </Card>
      )}

      {/* Step 3: Result */}
      {step === 3 && (
        <Card className="text-center py-10">
          {result?.success ? (
            <>
              <div className="flex justify-center mb-4">
                <div className="h-24 w-24 rounded-full bg-green-100 flex items-center justify-center">
                  <CheckCircle2 className="h-14 w-14 text-green-600" />
                </div>
              </div>
              <h2 className="text-2xl font-bold text-green-700 mb-2">Attendance Marked!</h2>
              <p className="text-gray-600">{result.message}</p>
              {result.confidence && (
                <p className="text-sm text-gray-400 mt-2">
                  Verification confidence: {(result.confidence * 100).toFixed(1)}%
                </p>
              )}
            </>
          ) : (
            <>
              <div className="flex justify-center mb-4">
                <div className="h-24 w-24 rounded-full bg-red-100 flex items-center justify-center">
                  <XCircle className="h-14 w-14 text-red-600" />
                </div>
              </div>
              <h2 className="text-2xl font-bold text-red-700 mb-2">Verification Failed</h2>
              <p className="text-gray-600">{result?.message}</p>
            </>
          )}
          <div className="mt-6 flex justify-center gap-4">
            <Button
              variant="outline"
              onClick={() => { setStep(1); setSessionCode(''); setResult(null); }}
            >
              Try Again
            </Button>
            <Button
              onClick={() => navigate('/my-profile')}
              className="bg-teal-600 hover:bg-teal-700"
            >
              Back to Dashboard
            </Button>
          </div>
        </Card>
      )}
    </div>
  );
}
