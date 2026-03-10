/**
 * Authentication service for ECES Frontend
 */

export interface User {
  id: string;
  username: string;
  email: string;
  full_name: string;
  role: 'super_admin' | 'admin' | 'matrix_editor' | 'user' | 'viewer';
  department?: string;
  is_active: boolean;
  created_at: string;
  last_login?: string;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface LoginResponse {
  access_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface UserPermissions {
  user: string;
  role: string;
  permissions: {
    can_view: boolean;
    can_use_recognition: boolean;
    can_use_conversion: boolean;
    can_view_matrix: boolean;
    can_edit_matrix: boolean;
    can_manage_users: boolean;
    can_access_admin: boolean;
  };
}

export interface PasswordChangeRequest {
  current_password: string;
  new_password: string;
}

export interface PasswordChangeResponse {
  success: boolean;
  message: string;
}

class AuthService {
  private baseURL = `${import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'}/api/auth`;
  private tokenKey = 'eces_token';
  private userKey = 'eces_user';

  // Get stored token
  getToken(): string | null {
    return localStorage.getItem(this.tokenKey);
  }

  // Get stored user
  getUser(): User | null {
    const userStr = localStorage.getItem(this.userKey);
    return userStr ? JSON.parse(userStr) : null;
  }

  // Check if user is authenticated
  isAuthenticated(): boolean {
    const token = this.getToken();
    const user = this.getUser();
    return !!(token && user);
  }

  // Check if user is Super Admin
  isSuperAdmin(): boolean {
    const user = this.getUser();
    return user?.role === 'super_admin';
  }

  // Login
  async login(credentials: LoginRequest): Promise<LoginResponse> {
    const response = await fetch(`${this.baseURL}/login`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(credentials),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Login failed');
    }

    const data: LoginResponse = await response.json();
    
    // Store token and user
    localStorage.setItem(this.tokenKey, data.access_token);
    localStorage.setItem(this.userKey, JSON.stringify(data.user));
    
    return data;
  }

  // Logout
  async logout(): Promise<void> {
    const token = this.getToken();
    
    if (token) {
      try {
        await fetch(`${this.baseURL}/logout`, {
          method: 'POST',
          headers: {
            'Authorization': `Bearer ${token}`,
          },
        });
      } catch (error) {
        console.warn('Logout request failed:', error);
      }
    }
    
    // Clear local storage
    localStorage.removeItem(this.tokenKey);
    localStorage.removeItem(this.userKey);
  }

  // Get current user info from server
  async getCurrentUser(): Promise<User> {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('No authentication token');
    }

    const response = await fetch(`${this.baseURL}/me`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      if (response.status === 401) {
        this.logout(); // Clear invalid token
      }
      throw new Error('Failed to get user info');
    }

    const user: User = await response.json();
    localStorage.setItem(this.userKey, JSON.stringify(user));
    return user;
  }

  // Get user permissions
  async getUserPermissions(): Promise<UserPermissions> {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('No authentication token');
    }

    const response = await fetch(`${this.baseURL}/permissions`, {
      headers: {
        'Authorization': `Bearer ${token}`,
      },
    });

    if (!response.ok) {
      throw new Error('Failed to get permissions');
    }

    return response.json();
  }

  // Get authorization header
  getAuthHeader(): Record<string, string> {
    const token = this.getToken();
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  }

  // Check if token is expired (basic check)
  isTokenExpired(): boolean {
    const user = this.getUser();
    if (!user) return true;

    // Simple check - in production you might want to decode JWT
    const now = Date.now();
    const loginTime = new Date(user.last_login || user.created_at).getTime();
    const eightHours = 8 * 60 * 60 * 1000; // 8 hours in milliseconds
    
    return (now - loginTime) > eightHours;
  }

  // Change password
  async changePassword(passwordData: PasswordChangeRequest): Promise<PasswordChangeResponse> {
    const token = this.getToken();
    
    if (!token) {
      throw new Error('No authentication token');
    }

    const response = await fetch(`${this.baseURL}/change-password`, {
      method: 'PUT',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${token}`,
      },
      body: JSON.stringify(passwordData),
    });

    if (!response.ok) {
      const error = await response.json();
      throw new Error(error.detail || 'Password change failed');
    }

    return response.json();
  }
}

export const authService = new AuthService();