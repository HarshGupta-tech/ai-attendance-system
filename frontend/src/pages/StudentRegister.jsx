import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuth } from '../contexts/AuthContext';
import { GraduationCap, Mail, Lock, User, Hash, Eye, EyeOff } from 'lucide-react';
import toast from 'react-hot-toast';
import Input from '../components/common/Input';
import Button from '../components/common/Button';

const StudentRegister = () => {
  const [formData, setFormData] = useState({
    student_id: '',
    roll_number: '',
    full_name: '',
    email: '',
    password: '',
    confirm_password: ''
  });
  const [showPassword, setShowPassword] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  
  const { register } = useAuth();
  const navigate = useNavigate();

  const handleChange = (e) => {
    setFormData({ ...formData, [e.target.id]: e.target.value });
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (formData.password !== formData.confirm_password) {
      toast.error('Passwords do not match');
      return;
    }
    
    setIsLoading(true);
    const result = await register({
      student_id: formData.student_id,
      roll_number: formData.roll_number,
      full_name: formData.full_name,
      email: formData.email,
      password: formData.password
    });
    setIsLoading(false);

    if (result.success) {
      toast.success('Registration successful! Please login.');
      navigate('/login');
    } else {
      toast.error(result.error || 'Registration failed');
    }
  };

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col justify-center py-12 sm:px-6 lg:px-8">
      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="flex justify-center">
          <div className="h-16 w-16 bg-teal-600 rounded-full flex items-center justify-center shadow-lg">
            <GraduationCap className="h-10 w-10 text-white" />
          </div>
        </div>
        <h2 className="mt-6 text-center text-3xl font-extrabold text-teal-900">
          Student Registration
        </h2>
        <p className="mt-2 text-center text-sm text-gray-600">
          Create your account
        </p>
      </div>

      <div className="mt-8 sm:mx-auto sm:w-full sm:max-w-md">
        <div className="bg-white py-8 px-4 shadow sm:rounded-lg sm:px-10 border border-gray-200">
          <form className="space-y-6" onSubmit={handleSubmit}>
            <Input
              id="student_id"
              label="Student ID (Username)"
              type="text"
              value={formData.student_id}
              onChange={handleChange}
              iconLeft={Hash}
              placeholder="e.g. S001"
              required
            />
            
            <Input
              id="roll_number"
              label="Roll Number"
              type="text"
              value={formData.roll_number}
              onChange={handleChange}
              iconLeft={Hash}
              placeholder="e.g. 101"
              required
            />
            
            <Input
              id="full_name"
              label="Full Name"
              type="text"
              value={formData.full_name}
              onChange={handleChange}
              iconLeft={User}
              placeholder="Enter your full name"
              required
            />
            
            <Input
              id="email"
              label="Email"
              type="email"
              value={formData.email}
              onChange={handleChange}
              iconLeft={Mail}
              placeholder="student@example.com"
              required
            />

            <div className="relative">
              <Input
                id="password"
                label="Password"
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={handleChange}
                iconLeft={Lock}
                placeholder="••••••••"
                required
              />
              <button
                type="button"
                className="absolute inset-y-0 right-0 pr-3 flex items-center top-7"
                onClick={() => setShowPassword(!showPassword)}
              >
                {showPassword ? (
                  <EyeOff className="h-5 w-5 text-gray-400" />
                ) : (
                  <Eye className="h-5 w-5 text-gray-400" />
                )}
              </button>
            </div>
            
            <Input
              id="confirm_password"
              label="Confirm Password"
              type={showPassword ? 'text' : 'password'}
              value={formData.confirm_password}
              onChange={handleChange}
              iconLeft={Lock}
              placeholder="••••••••"
              required
            />

            <div>
              <Button
                type="submit"
                fullWidth
                size="lg"
                isLoading={isLoading}
                className="bg-teal-600 hover:bg-teal-700 focus:ring-teal-500"
              >
                Register
              </Button>
            </div>
          </form>

          <div className="mt-6 text-center text-sm">
            <p className="text-gray-600">
              Already have an account?{' '}
              <a href="/login" className="font-medium text-teal-600 hover:text-teal-500">
                Log in here
              </a>
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default StudentRegister;
