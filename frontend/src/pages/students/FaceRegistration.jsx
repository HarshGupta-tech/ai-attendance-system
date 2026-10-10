import React, { useState, useEffect, useRef } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Camera, Check, AlertCircle, RefreshCw } from 'lucide-react';
import api from '../../utils/api';
import { Button, Card } from '../../components/common';
import toast from 'react-hot-toast';

export default function FaceRegistration() {
  const params = useParams();
  const id = params.id || "me";
  const navigate = useNavigate();
  
  const [student, setStudent] = useState(null);
  const [consentGiven, setConsentGiven] = useState(false);
  const [streamActive, setStreamActive] = useState(false);
  const [capturedImages, setCapturedImages] = useState([]);
  const [isSubmitting, setIsSubmitting] = useState(false);
  
  const videoRef = useRef(null);
  const canvasRef = useRef(null);
  const REQUIRED_SAMPLES = 5;

  useEffect(() => {
    api.get(`/students/${id}`).then(res => setStudent(res.data)).catch(err => {
      toast.error('Failed to load student');
      navigate(id === 'me' ? '/my-profile' : '/students');
    });
    
    return () => stopCamera(); // Cleanup on unmount
  }, [id]);

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

  const handleConsent = () => {
    setConsentGiven(true);
    startCamera();
  };

  const captureFrame = () => {
    if (!videoRef.current || capturedImages.length >= REQUIRED_SAMPLES) return;
    
    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    canvas.width = videoRef.current.videoWidth;
    canvas.height = videoRef.current.videoHeight;
    ctx.drawImage(videoRef.current, 0, 0, canvas.width, canvas.height);
    
    const base64Image = canvas.toDataURL('image/jpeg', 0.8);
    setCapturedImages(prev => [...prev, base64Image]);
  };

  const removeImage = (index) => {
    setCapturedImages(prev => prev.filter((_, i) => i !== index));
  };

  const handleSubmit = async () => {
    if (capturedImages.length < REQUIRED_SAMPLES) {
      toast.error(`Please capture at least ${REQUIRED_SAMPLES} samples`);
      return;
    }
    
    setIsSubmitting(true);
    try {
      await api.post(`/students/${id}/face-register`, { images: capturedImages });
      toast.success('Face registered successfully!');
      stopCamera();
      navigate(id === 'me' ? '/my-profile' : `/students/${id}`);
    } catch (err) {
      toast.error(err.response?.data?.message || 'Failed to register face');
      setIsSubmitting(false);
    }
  };

  if (!student) return <div className="p-6">Loading...</div>;

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-2xl font-bold text-gray-900">Face Registration for {student.fullName}</h1>
        <Button variant="outline" onClick={() => navigate(`/students/${id}`)}>Back to Profile</Button>
      </div>

      {!consentGiven ? (
        <Card className="text-center p-8 max-w-2xl mx-auto mt-10 border-indigo-100 border-2">
          <AlertCircle className="mx-auto text-indigo-500 w-16 h-16 mb-4" />
          <h2 className="text-2xl font-semibold mb-4">Privacy & Consent</h2>
          <p className="text-gray-600 mb-8 text-lg">
            This system will capture and store facial biometric data for the sole purpose of automated attendance tracking. By proceeding, you consent to the collection, processing, and secure storage of this biometric data.
          </p>
          <div className="flex justify-center gap-4">
            <Button variant="outline" onClick={() => navigate(id === 'me' ? '/my-profile' : `/students/${id}`)}>Decline & Cancel</Button>
            <Button onClick={handleConsent} className="bg-indigo-600 text-white">I Consent, Proceed</Button>
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {/* Camera View */}
          <Card className="flex flex-col">
            <h3 className="text-lg font-semibold mb-4">Live Camera Feed</h3>
            <div className="relative bg-black rounded-lg overflow-hidden flex-1 flex items-center justify-center min-h-[360px]">
              <video 
                ref={videoRef} 
                autoPlay 
                playsInline 
                className="w-full h-full object-cover"
                style={{ transform: 'scaleX(-1)' }} // mirror effect
              />
              <canvas ref={canvasRef} className="hidden" />
              
              {/* Overlay for face guide */}
              <div className="absolute inset-0 border-4 border-dashed border-white/30 m-12 rounded-full flex items-center justify-center pointer-events-none">
                {/* Simulated face detection box can go here */}
              </div>
            </div>
            
            <div className="mt-4 flex justify-between items-center">
              <p className="text-sm text-gray-500">Please look directly at the camera in good lighting.</p>
              <Button 
                onClick={captureFrame} 
                disabled={capturedImages.length >= REQUIRED_SAMPLES || !streamActive}
                className="flex items-center gap-2"
              >
                <Camera size={16} /> Capture Photo
              </Button>
            </div>
          </Card>

          {/* Captured Samples */}
          <Card className="flex flex-col">
            <h3 className="text-lg font-semibold mb-4">Captured Samples</h3>
            <div className="mb-4">
              <div className="flex justify-between text-sm mb-1">
                <span>Progress: {capturedImages.length} / {REQUIRED_SAMPLES}</span>
                <span className={capturedImages.length >= REQUIRED_SAMPLES ? 'text-green-600 font-medium' : 'text-gray-500'}>
                  {capturedImages.length >= REQUIRED_SAMPLES ? 'Ready to register' : 'Need more samples'}
                </span>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-2">
                <div 
                  className={`h-2 rounded-full ${capturedImages.length >= REQUIRED_SAMPLES ? 'bg-green-500' : 'bg-indigo-500'}`} 
                  style={{ width: `${Math.min(100, (capturedImages.length / REQUIRED_SAMPLES) * 100)}%` }}
                ></div>
              </div>
            </div>

            <div className="grid grid-cols-3 gap-3 flex-1 auto-rows-max">
              {capturedImages.map((img, idx) => (
                <div key={idx} className="relative group rounded-md overflow-hidden border">
                  <img src={img} alt={`Sample ${idx+1}`} className="w-full h-24 object-cover" style={{ transform: 'scaleX(-1)' }} />
                  <div className="absolute inset-0 bg-black/50 opacity-0 group-hover:opacity-100 flex items-center justify-center transition-opacity">
                    <button onClick={() => removeImage(idx)} className="text-white text-xs bg-red-600 px-2 py-1 rounded">Remove</button>
                  </div>
                </div>
              ))}
              {/* Empty placeholders */}
              {Array.from({ length: Math.max(0, REQUIRED_SAMPLES - capturedImages.length) }).map((_, idx) => (
                <div key={`empty-${idx}`} className="h-24 bg-gray-100 rounded-md border border-dashed border-gray-300 flex items-center justify-center text-gray-400">
                  <Camera size={24} />
                </div>
              ))}
            </div>

            <div className="mt-4 pt-4 border-t flex justify-end">
              <Button 
                onClick={handleSubmit} 
                disabled={capturedImages.length < REQUIRED_SAMPLES || isSubmitting}
                className="w-full flex justify-center items-center gap-2 bg-green-600 hover:bg-green-700 text-white"
              >
                {isSubmitting ? <RefreshCw className="animate-spin" size={16} /> : <Check size={16} />}
                {isSubmitting ? 'Processing...' : 'Register Face Data'}
              </Button>
            </div>
          </Card>
        </div>
      )}
    </div>
  );
}
