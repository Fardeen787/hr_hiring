# Frontend Integration Examples

## 🚀 React.js Integration

### 1. Install Dependencies
```bash
npm install axios firebase
```

### 2. API Service (apiService.js)
```javascript
import axios from 'axios';

// Configure base URL
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

const apiClient = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Add token to requests automatically
apiClient.interceptors.request.use((config) => {
  const token = localStorage.getItem('access_token');
  if (token) {
    config.headers.Authorization = `Bearer ${token}`;
  }
  return config;
});

// Handle token refresh on 401 errors
apiClient.interceptors.response.use(
  (response) => response,
  async (error) => {
    if (error.response?.status === 401) {
      // Try to refresh token
      const refreshToken = localStorage.getItem('refresh_token');
      if (refreshToken) {
        try {
          const response = await axios.post(`${API_BASE_URL}/api/auth/refresh`, {
            refresh_token: refreshToken
          });
          const { access_token } = response.data;
          localStorage.setItem('access_token', access_token);
          
          // Retry original request
          error.config.headers.Authorization = `Bearer ${access_token}`;
          return axios.request(error.config);
        } catch (refreshError) {
          // Refresh failed, redirect to login
          localStorage.removeItem('access_token');
          localStorage.removeItem('refresh_token');
          window.location.href = '/login';
        }
      }
    }
    return Promise.reject(error);
  }
);

export default apiClient;
```

### 3. Authentication Context (AuthContext.js)
```javascript
import React, { createContext, useContext, useState, useEffect } from 'react';
import apiClient from './apiService';

const AuthContext = createContext();

export const useAuth = () => {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error('useAuth must be used within an AuthProvider');
  }
  return context;
};

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkAuthStatus();
  }, []);

  const checkAuthStatus = async () => {
    const token = localStorage.getItem('access_token');
    if (token) {
      try {
        const response = await apiClient.get('/api/users/me');
        setUser(response.data);
      } catch (error) {
        localStorage.removeItem('access_token');
        localStorage.removeItem('refresh_token');
      }
    }
    setLoading(false);
  };

  const login = async (email, password) => {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/login`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();
      
      if (response.ok) {
        localStorage.setItem('access_token', data.access_token);
        localStorage.setItem('refresh_token', data.refresh_token);
        await checkAuthStatus();
        return { success: true };
      } else {
        return { success: false, error: data.detail };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  };

  const signup = async (userData) => {
    try {
      const response = await apiClient.post('/api/auth/signup', userData);
      localStorage.setItem('access_token', response.data.access_token);
      localStorage.setItem('refresh_token', response.data.refresh_token);
      await checkAuthStatus();
      return { success: true };
    } catch (error) {
      return { 
        success: false, 
        error: error.response?.data?.detail || 'Signup failed' 
      };
    }
  };

  const logout = async () => {
    try {
      await apiClient.post('/api/auth/logout');
    } catch (error) {
      console.error('Logout error:', error);
    } finally {
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
      setUser(null);
    }
  };

  const value = {
    user,
    login,
    signup,
    logout,
    loading,
  };

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
};
```

### 4. Firebase Integration (firebaseAuth.js)
```javascript
import { initializeApp } from 'firebase/app';
import { getAuth, GoogleAuthProvider, signInWithPopup } from 'firebase/auth';

const firebaseConfig = {
  apiKey: "AIzaSyDGcGLNQZpsgDOP7wVLibK7a_9OsXehEKI",
  authDomain: "login-signup-auth-8e3e0.firebaseapp.com",
  projectId: "login-signup-auth-8e3e0",
  storageBucket: "login-signup-auth-8e3e0.firebasestorage.app",
  messagingSenderId: "344732054033",
  appId: "1:344732054033:web:9126babe559ccc127637b0",
  measurementId: "G-TTLS9PTZZE"
};

const app = initializeApp(firebaseConfig);
export const auth = getAuth(app);
export const googleProvider = new GoogleAuthProvider();

export const signInWithGoogle = async () => {
  try {
    const result = await signInWithPopup(auth, googleProvider);
    const idToken = await result.user.getIdToken();
    
    // Send to your backend
    const response = await fetch(`${process.env.REACT_APP_API_URL}/api/auth/firebase-login`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ id_token: idToken })
    });
    
    const data = await response.json();
    
    if (response.ok) {
      localStorage.setItem('access_token', data.access_token);
      localStorage.setItem('refresh_token', data.refresh_token);
      return { success: true, user: result.user };
    } else {
      return { success: false, error: data.detail };
    }
  } catch (error) {
    return { success: false, error: error.message };
  }
};
```

### 5. Login Component (Login.js)
```javascript
import React, { useState } from 'react';
import { useAuth } from './AuthContext';
import { signInWithGoogle } from './firebaseAuth';

const Login = () => {
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const { login } = useAuth();

  const handleEmailLogin = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    const result = await login(email, password);
    
    if (result.success) {
      // Redirect to dashboard
      window.location.href = '/dashboard';
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  const handleGoogleLogin = async () => {
    setLoading(true);
    setError('');
    
    const result = await signInWithGoogle();
    
    if (result.success) {
      window.location.href = '/dashboard';
    } else {
      setError(result.error);
    }
    
    setLoading(false);
  };

  return (
    <div className="login-container">
      <h2>Login</h2>
      
      {error && <div className="error">{error}</div>}
      
      <form onSubmit={handleEmailLogin}>
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          required
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          required
        />
        <button type="submit" disabled={loading}>
          {loading ? 'Logging in...' : 'Login'}
        </button>
      </form>
      
      <div className="divider">OR</div>
      
      <button onClick={handleGoogleLogin} disabled={loading}>
        Sign in with Google
      </button>
    </div>
  );
};

export default Login;
```

## 🚀 Vue.js Integration

### 1. Install Dependencies
```bash
npm install axios firebase pinia
```

### 2. Pinia Store (stores/auth.js)
```javascript
import { defineStore } from 'pinia';
import axios from 'axios';

const API_BASE_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000';

export const useAuthStore = defineStore('auth', {
  state: () => ({
    user: null,
    token: localStorage.getItem('access_token'),
    loading: false,
  }),

  getters: {
    isAuthenticated: (state) => !!state.token,
    userRole: (state) => state.user?.role,
  },

  actions: {
    async login(email, password) {
      this.loading = true;
      try {
        const formData = new FormData();
        formData.append('username', email);
        formData.append('password', password);

        const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
          method: 'POST',
          body: formData,
        });

        const data = await response.json();

        if (response.ok) {
          this.token = data.access_token;
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('refresh_token', data.refresh_token);
          await this.fetchUser();
          return { success: true };
        } else {
          return { success: false, error: data.detail };
        }
      } catch (error) {
        return { success: false, error: 'Network error' };
      } finally {
        this.loading = false;
      }
    },

    async fetchUser() {
      if (!this.token) return;

      try {
        const response = await axios.get(`${API_BASE_URL}/api/users/me`, {
          headers: { Authorization: `Bearer ${this.token}` },
        });
        this.user = response.data;
      } catch (error) {
        this.logout();
      }
    },

    logout() {
      this.user = null;
      this.token = null;
      localStorage.removeItem('access_token');
      localStorage.removeItem('refresh_token');
    },
  },
});
```

## 🚀 Angular Integration

### 1. Auth Service (auth.service.ts)
```typescript
import { Injectable } from '@angular/core';
import { HttpClient, HttpHeaders } from '@angular/common/http';
import { BehaviorSubject, Observable } from 'rxjs';
import { map } from 'rxjs/operators';

interface User {
  id: number;
  email: string;
  name: string;
  role: string;
  permissions: string[];
}

interface AuthResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

@Injectable({
  providedIn: 'root'
})
export class AuthService {
  private apiUrl = environment.apiUrl || 'http://localhost:8000';
  private currentUserSubject = new BehaviorSubject<User | null>(null);
  public currentUser$ = this.currentUserSubject.asObservable();

  constructor(private http: HttpClient) {
    this.checkAuthStatus();
  }

  private checkAuthStatus(): void {
    const token = localStorage.getItem('access_token');
    if (token) {
      this.getCurrentUser().subscribe({
        next: (user) => this.currentUserSubject.next(user),
        error: () => this.logout()
      });
    }
  }

  login(email: string, password: string): Observable<boolean> {
    const formData = new FormData();
    formData.append('username', email);
    formData.append('password', password);

    return this.http.post<AuthResponse>(`${this.apiUrl}/api/auth/login`, formData)
      .pipe(
        map(response => {
          localStorage.setItem('access_token', response.access_token);
          localStorage.setItem('refresh_token', response.refresh_token);
          this.checkAuthStatus();
          return true;
        })
      );
  }

  getCurrentUser(): Observable<User> {
    return this.http.get<User>(`${this.apiUrl}/api/users/me`);
  }

  logout(): void {
    localStorage.removeItem('access_token');
    localStorage.removeItem('refresh_token');
    this.currentUserSubject.next(null);
  }

  get isAuthenticated(): boolean {
    return !!localStorage.getItem('access_token');
  }
}
```

## 📱 React Native Integration

### 1. Install Dependencies
```bash
npm install @react-native-async-storage/async-storage axios
```

### 2. Auth Service (authService.js)
```javascript
import AsyncStorage from '@react-native-async-storage/async-storage';
import axios from 'axios';

const API_BASE_URL = 'https://your-deployed-api.com';

class AuthService {
  async login(email, password) {
    try {
      const formData = new FormData();
      formData.append('username', email);
      formData.append('password', password);

      const response = await fetch(`${API_BASE_URL}/api/auth/login`, {
        method: 'POST',
        body: formData,
      });

      const data = await response.json();

      if (response.ok) {
        await AsyncStorage.setItem('access_token', data.access_token);
        await AsyncStorage.setItem('refresh_token', data.refresh_token);
        return { success: true };
      } else {
        return { success: false, error: data.detail };
      }
    } catch (error) {
      return { success: false, error: 'Network error' };
    }
  }

  async getCurrentUser() {
    try {
      const token = await AsyncStorage.getItem('access_token');
      if (!token) return null;

      const response = await axios.get(`${API_BASE_URL}/api/users/me`, {
        headers: { Authorization: `Bearer ${token}` },
      });

      return response.data;
    } catch (error) {
      await this.logout();
      return null;
    }
  }

  async logout() {
    await AsyncStorage.removeItem('access_token');
    await AsyncStorage.removeItem('refresh_token');
  }
}

export default new AuthService();
```

## 🔧 Environment Variables

### React (.env)
```env
REACT_APP_API_URL=https://your-deployed-api.com
REACT_APP_FIREBASE_API_KEY=AIzaSyDGcGLNQZpsgDOP7wVLibK7a_9OsXehEKI
REACT_APP_FIREBASE_AUTH_DOMAIN=login-signup-auth-8e3e0.firebaseapp.com
REACT_APP_FIREBASE_PROJECT_ID=login-signup-auth-8e3e0
```

### Vue (.env)
```env
VITE_API_URL=https://your-deployed-api.com
VITE_FIREBASE_API_KEY=AIzaSyDGcGLNQZpsgDOP7wVLibK7a_9OsXehEKI
VITE_FIREBASE_AUTH_DOMAIN=login-signup-auth-8e3e0.firebaseapp.com
```

### Angular (environment.ts)
```typescript
export const environment = {
  production: false,
  apiUrl: 'https://your-deployed-api.com',
  firebase: {
    apiKey: 'AIzaSyDGcGLNQZpsgDOP7wVLibK7a_9OsXehEKI',
    authDomain: 'login-signup-auth-8e3e0.firebaseapp.com',
    projectId: 'login-signup-auth-8e3e0',
  }
};
```
