import axios from 'axios';

const API_BASE_URL = '/api';
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 45000,
});

// Response interceptor to unwrap data envelope safely
api.interceptors.response.use(
  (response) => response.data,
  (error) => {
    if (axios.isCancel(error)) {
      return Promise.reject(new Error('Request cancelled'));
    }
    const errorMsg = error.response?.data?.message || error.response?.data?.errors?.[0] || error.message || 'API Request Failed';
    return Promise.reject(new Error(errorMsg));
  }
);

export const SystemAPI = {
  getHealth: () => api.get('/health'),
  getStatus: () => api.get('/system/status'),
  getVersion: () => api.get('/system/version'),
  getMetrics: () => api.get('/metrics'),
  getIntegrity: () => api.get('/integrity'),
  getArchitecture: () => api.get('/architecture'),
  getDiagnostics: () => api.get('/diagnostics'),
};

export const PipelineAPI = {
  run: (accountId, autoApproveHitl = true, prompt = '', signal) =>
    api.post('/pipeline/run', { account_id: accountId, auto_approve_hitl: autoApproveHitl, prompt }, { signal }),
  stream: (accountId, prompt, onMessage, onError, onComplete, signal) => {
    const url = `${API_BASE_URL}/pipeline/stream?account_id=${accountId}&prompt=${encodeURIComponent(prompt)}`;
    const source = new EventSource(url);

    // Track whether the pipeline delivered a Final Response before the
    // connection closed. EventSource fires onerror on ANY close — including
    // a normal server-side stream end — so we must distinguish between a
    // real network failure and a clean completion.
    let receivedFinalResponse = false;

    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Mark success as soon as the Final Response stage arrives.
        if (data.stage === 'Final Response' || (data.payload && data.payload.response)) {
          receivedFinalResponse = true;
        }

        onMessage(data);
      } catch (err) {
        console.error("Failed to parse SSE data", err);
      }
    };

    source.onerror = (err) => {
      source.close();
      if (receivedFinalResponse) {
        // Stream ended normally after delivering the response — not an error.
        if (onComplete) onComplete();
      } else {
        // Real failure: stream closed without ever sending a Final Response.
        if (onError) onError(err);
      }
    };

    if (signal) {
      signal.addEventListener('abort', () => {
        source.close();
      });
    }

    return source;
  },
  getHistory: () => api.get('/pipeline/history'),
  getStatus: (runId) => api.get(`/pipeline/status/${runId}`),
};

export const AgentsAPI = {
  list: () => api.get('/agents'),
  getDetails: (agentId) => api.get(`/agents/${agentId}`),
  getStatus: (agentId) => api.get(`/agents/${agentId}/status`),
};

export const PoliciesAPI = {
  list: () => api.get('/policies'),
  getSchema: () => api.get('/policies/schema'),
  getPolicy: (agentId) => api.get(`/policies/${agentId}`),
  validate: (policyYamlContent) => api.post('/policies/validate', { policy_yaml_content: policyYamlContent }),
  deploy: (agentId, policyYamlContent) => api.post('/policies/deploy', { agent_id: agentId, policy_yaml_content: policyYamlContent }),
};

export const GlobalVersionsAPI = {
  list: () => api.get('/versions'),
  getCurrent: () => api.get('/versions/current'),
  getVersion: (versionNum) => api.get(`/versions/${versionNum}`),
  rollback: (versionNum) => api.post(`/versions/${versionNum}/rollback`),
};

export const AuditAPI = {
  getRecent: () => api.get('/audit'),
  exportLogs: () => api.get('/audit/export'),
  search: (searchParams) => api.post('/audit/search', searchParams),
};

export const ReportsAPI = {
  list: () => api.get('/reports'),
  getReport: (reportId) => api.get(`/reports/${reportId}`),
  download: (reportId) => api.get(`/reports/download/${reportId}`),
};

export const StatsAPI = {
  getAgentStats: () => api.get('/stats/agents'),
  getToolStats: () => api.get('/stats/tools'),
};

export const DemoAPI = {
  getTools: () => api.get('/demo/tools'),
  toggleTool: (toolKey, enabled) => api.post('/demo/tool/toggle', { tool_key: toolKey, enabled }),
  toggleSafeMode: (enabled) => api.post('/demo/safemode/toggle', { enabled }),
  runSample: () => api.post('/demo/run-sample'),
  resetDemo: () => api.post('/demo/reset'),
};

export const HitlAPI = {
  approve: (requestId) => api.post(`/hitl/approve/${requestId}`),
  reject: (requestId) => api.post(`/hitl/reject/${requestId}`),
};

export default api;
