import React, { useState, useEffect } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from './ui/Card';
import { Button } from './ui/Button';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/Select';
import { Badge } from './ui/Badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from './ui/Tabs';
import { 
  AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell
} from 'recharts';
import { 
  Activity, Users, Database, TrendingUp, Download, 
  RefreshCw, Calendar, Search, FileText, Settings
} from 'lucide-react';
import { authService } from '../services/auth';
import './Analytics.css';

interface AnalyticsData {
  summary: any;
  popularStrings: any[];
  activeSessions: any;
  health: any;
}

interface UsageSummary {
  total_queries: number;
  unique_users: number;
  unique_strings: number;
  avg_processing_time: number;
  success_rate: number;
  daily_trend: Array<{
    date_only: string;
    queries: number;
    active_users: number;
    avg_time: number;
  }>;
  top_users: Array<{
    username: string;
    query_count: number;
    unique_strings_tested: number;
    avg_processing_time: number;
  }>;
  version_distribution: Array<{
    version: string;
    count: number;
    percentage: number;
  }>;
}

const Analytics: React.FC = () => {
  const [data, setData] = useState<AnalyticsData | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedPeriod, setSelectedPeriod] = useState('30');
  const [refreshing, setRefreshing] = useState(false);

  const fetchAnalytics = async () => {
    try {
      setLoading(true);
      setError(null);

      // Check authentication using auth service
      if (!authService.isAuthenticated()) {
        throw new Error('Token di autenticazione non trovato');
      }

      const authHeaders = authService.getAuthHeader();
      const headers = {
        ...authHeaders,
        'Content-Type': 'application/json'
      };

      // Fetch multiple endpoints in parallel
      const [summaryRes, stringsRes, sessionsRes, healthRes] = await Promise.all([
        fetch(`/api/analytics/usage/summary?days=${selectedPeriod}`, { headers }),
        fetch('/api/analytics/strings/popular?limit=10', { headers }),
        fetch('/api/analytics/sessions/active', { headers }),
        fetch('/api/analytics/health', { headers })
      ]);

      if (!summaryRes.ok) {
        if (summaryRes.status === 401) {
          throw new Error('Token di autenticazione non trovato');
        }
        throw new Error(`Errore: ${summaryRes.status}`);
      }

      const [summary, strings, sessions, health] = await Promise.all([
        summaryRes.json(),
        stringsRes.json(),
        sessionsRes.json(),
        healthRes.json()
      ]);

      setData({
        summary: summary.data,
        popularStrings: strings.data || [],
        activeSessions: sessions.data,
        health: health.data
      });

    } catch (err) {
      console.error('Errore nel caricamento analytics:', err);
      setError(err instanceof Error ? err.message : 'Errore sconosciuto');
    } finally {
      setLoading(false);
      setRefreshing(false);
    }
  };

  const handleRefresh = async () => {
    setRefreshing(true);
    await fetchAnalytics();
  };

  const exportData = async (format: 'json' | 'csv') => {
    try {
      if (!authService.isAuthenticated()) {
        throw new Error('Utente non autenticato');
      }

      const authHeaders = authService.getAuthHeader();
      const response = await fetch(`/api/analytics/export/research?format=${format}`, {
        headers: {
          ...authHeaders,
          'Content-Type': 'application/json'
        }
      });

      if (!response.ok) {
        throw new Error('Errore nell\'export dei dati');
      }

      if (format === 'csv') {
        const blob = await response.blob();
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `eces_analytics_${new Date().toISOString().split('T')[0]}.csv`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      } else {
        const data = await response.json();
        const blob = new Blob([JSON.stringify(data, null, 2)], { type: 'application/json' });
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `eces_analytics_${new Date().toISOString().split('T')[0]}.json`;
        document.body.appendChild(a);
        a.click();
        window.URL.revokeObjectURL(url);
        document.body.removeChild(a);
      }
    } catch (err) {
      console.error('Errore nell\'export:', err);
      alert('Errore nell\'export dei dati');
    }
  };

  useEffect(() => {
    // Check if user is Super Admin before loading analytics
    if (!authService.isAuthenticated() || !authService.isSuperAdmin()) {
      setError('Accesso negato - Solo Super Admin');
      setLoading(false);
      return;
    }
    
    fetchAnalytics();
  }, [selectedPeriod]);

  if (loading && !data) {
    return (
      <div className="analytics-container">
        <div className="analytics-loading">
          <RefreshCw className="animate-spin" size={32} />
          <p>Caricamento...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="analytics-container">
        <div className="analytics-error">
          <h3>Errore nel caricamento</h3>
          <p>{error}</p>
          <Button onClick={fetchAnalytics}>Riprova</Button>
        </div>
      </div>
    );
  }

  const summary: UsageSummary = data?.summary || {};
  const COLORS = ['#0088FE', '#00C49F', '#FFBB28', '#FF8042', '#8884D8'];

  return (
    <div className="analytics-container">
      <div className="analytics-header">
        <div className="analytics-title">
          <Activity size={24} />
          <h1>Dashboard Analytics</h1>
          <Badge variant="secondary">Super Admin</Badge>
        </div>
        
        <div className="analytics-controls">
          <Select value={selectedPeriod} onValueChange={setSelectedPeriod}>
            <SelectTrigger className="period-select">
              <Calendar size={16} />
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="7">Ultimi 7 giorni</SelectItem>
              <SelectItem value="30">Ultimi 30 giorni</SelectItem>
              <SelectItem value="90">Ultimi 90 giorni</SelectItem>
              <SelectItem value="365">Ultimo anno</SelectItem>
            </SelectContent>
          </Select>

          <Button 
            variant="outline" 
            onClick={handleRefresh}
            disabled={refreshing}
          >
            <RefreshCw className={refreshing ? 'animate-spin' : ''} size={16} />
            Aggiorna
          </Button>

          <Button 
            variant="outline" 
            onClick={() => exportData('csv')}
          >
            <Download size={16} />
            Esporta CSV
          </Button>
        </div>
      </div>

      {/* Overview Cards */}
      <div className="analytics-overview">
        <Card>
          <CardHeader>
            <CardTitle>
              <Search size={20} />
              Query Totali
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="metric-value">{summary.total_queries?.toLocaleString() || 0}</div>
            <div className="metric-label">Riconoscimenti EURING</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              <Users size={20} />
              Utenti Attivi
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="metric-value">{summary.unique_users || 0}</div>
            <div className="metric-label">Utenti unici</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              <FileText size={20} />
              Stringhe Testate
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="metric-value">{summary.unique_strings || 0}</div>
            <div className="metric-label">Stringhe uniche</div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>
              <TrendingUp size={20} />
              Tasso di Successo
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="metric-value">{summary.success_rate?.toFixed(1) || 0}%</div>
            <div className="metric-label">
              Tempo medio: {summary.avg_processing_time?.toFixed(0) || 0}ms
            </div>
          </CardContent>
        </Card>
      </div>

      <Tabs defaultValue="trends" className="analytics-tabs">
        <TabsList>
          <TabsTrigger value="trends">Trend Temporali</TabsTrigger>
          <TabsTrigger value="users">Utenti</TabsTrigger>
          <TabsTrigger value="strings">Stringhe Popolari</TabsTrigger>
          <TabsTrigger value="versions">Versioni EURING</TabsTrigger>
          <TabsTrigger value="system">Sistema</TabsTrigger>
        </TabsList>

        <TabsContent value="trends">
          <Card>
            <CardHeader>
              <CardTitle>Trend Query Giornaliere</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <AreaChart data={summary.daily_trend || []}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis 
                    dataKey="date_only" 
                    tickFormatter={(value) => new Date(value).toLocaleDateString('it-IT', { month: 'short', day: 'numeric' })}
                  />
                  <YAxis />
                  <Tooltip 
                    labelFormatter={(value) => new Date(value).toLocaleDateString('it-IT')}
                    formatter={(value, name) => [value, name === 'queries' ? 'Query' : 'Utenti Attivi']}
                  />
                  <Area type="monotone" dataKey="queries" stackId="1" stroke="#0088FE" fill="#0088FE" fillOpacity={0.6} />
                  <Area type="monotone" dataKey="active_users" stackId="2" stroke="#00C49F" fill="#00C49F" fillOpacity={0.6} />
                </AreaChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="users">
          <Card>
            <CardHeader>
              <CardTitle>Top Utenti Attivi</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="users-table">
                <div className="table-header">
                  <span>Utente</span>
                  <span>Query</span>
                  <span>Stringhe Uniche</span>
                  <span>Tempo Medio</span>
                </div>
                {summary.top_users?.map((user, index) => (
                  <div key={user.username} className="table-row">
                    <span className="user-name">
                      <Badge variant={index === 0 ? "default" : "secondary"}>
                        #{index + 1}
                      </Badge>
                      {user.username}
                    </span>
                    <span>{user.query_count}</span>
                    <span>{user.unique_strings_tested}</span>
                    <span>{user.avg_processing_time?.toFixed(0)}ms</span>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="strings">
          <Card>
            <CardHeader>
              <CardTitle>Stringhe Più Testate</CardTitle>
            </CardHeader>
            <CardContent>
              <div className="strings-list">
                {data?.popularStrings?.map((string, index) => (
                  <div key={index} className="string-item">
                    <div className="string-header">
                      <Badge variant="outline">#{index + 1}</Badge>
                      <span className="string-text">{string.original_string}</span>
                      <Badge variant={string.success_rate > 80 ? "default" : "secondary"}>
                        {string.success_rate}% successo
                      </Badge>
                    </div>
                    <div className="string-stats">
                      <span>{string.total_queries} query</span>
                      <span>Versione: {string.most_common_version || 'N/A'}</span>
                      <span>Lunghezza: {string.string_length} caratteri</span>
                    </div>
                  </div>
                ))}
              </div>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="versions">
          <Card>
            <CardHeader>
              <CardTitle>Distribuzione Versioni EURING</CardTitle>
            </CardHeader>
            <CardContent>
              <ResponsiveContainer width="100%" height={300}>
                <PieChart>
                  <Pie
                    data={summary.version_distribution || []}
                    cx="50%"
                    cy="50%"
                    labelLine={false}
                    label={({ name, value }) => `${name}: ${value}`}
                    outerRadius={80}
                    fill="#8884d8"
                    dataKey="count"
                  >
                    {summary.version_distribution?.map((_, index) => (
                      <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                    ))}
                  </Pie>
                  <Tooltip />
                </PieChart>
              </ResponsiveContainer>
            </CardContent>
          </Card>
        </TabsContent>

        <TabsContent value="system">
          <div className="system-grid">
            <Card>
              <CardHeader>
                <CardTitle>
                  <Database size={20} />
                  Stato Database
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="system-status">
                  <Badge variant={data?.health?.database?.connected ? "default" : "destructive"}>
                    {data?.health?.database?.connected ? 'Connesso' : 'Disconnesso'}
                  </Badge>
                  <div className="status-details">
                    <p>Abilitato: {data?.health?.database?.enabled ? 'Sì' : 'No'}</p>
                    <p>Test Query: {data?.health?.database?.test_query || 'N/A'}</p>
                  </div>
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>
                  <Activity size={20} />
                  Sessioni Attive
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="metric-value">{data?.activeSessions?.active_sessions || 0}</div>
                <div className="metric-label">
                  {data?.activeSessions?.pending_logs || 0} log in coda
                </div>
              </CardContent>
            </Card>

            <Card>
              <CardHeader>
                <CardTitle>
                  <Settings size={20} />
                  Azioni Manutenzione
                </CardTitle>
              </CardHeader>
              <CardContent>
                <div className="maintenance-actions">
                  <Button variant="outline" size="sm">
                    Sincronizza Database
                  </Button>
                  <Button variant="outline" size="sm">
                    Aggiorna Statistiche
                  </Button>
                  <Button variant="outline" size="sm">
                    Pulizia Dati Vecchi
                  </Button>
                </div>
              </CardContent>
            </Card>
          </div>
        </TabsContent>
      </Tabs>
    </div>
  );
};

export default Analytics;