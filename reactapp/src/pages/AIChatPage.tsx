import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useMutation, useQuery } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Database, Loader2, RefreshCw, Sparkles } from 'lucide-react';
import dayjs from 'dayjs';

import { chatWithAI, triggerReindex } from '../api/ai';
import { fetchEmployees } from '../api/users';
import { fetchProjects } from '../api/projects';
import type {
  ChatQueryResponse
} from '../types/api';
import { Card, SectionHeader } from '../components/common';
import { ChatMessage, PresetButton } from '../components/ai';
import { useAuth } from '../context/AuthContext';

interface ConversationEntry {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
}

function buildTimestamp() {
  return dayjs().format('MMM D, YYYY • h:mm A');
}

function generatePresetPrompts(employees: string[], projects: string[]) {
  const currentMonth = dayjs().format('MMMM YYYY');
  const nextMonth = dayjs().add(1, 'month').format('MMMM YYYY');
  const currentMonthOnly = dayjs().format('MMMM');
  
  const defaultPrompts = [
    {
      label: 'Show employees with availability',
      description: 'Find team members who have capacity for new work.',
      prompt: `Which employees have less than 80% FTE allocation in ${currentMonth}? Show me their names, current allocations, and available hours.`
    },
    {
      label: 'Check project staffing levels',
      description: 'Review current allocation across active projects.',
      prompt: `List all active projects with their staffing levels for ${currentMonth}. Include project names, assigned employees, and utilization percentages.`
    },
    {
      label: 'Identify over-allocated employees',
      description: 'Find team members who may be overcommitted.',
      prompt: `Which employees are allocated over 100% FTE in ${currentMonth}? List their names, total hours, FTE percentages, and which projects they're assigned to.`
    }
  ];

  // If we have employees, customize the first prompt
  if (employees.length > 0) {
    const employeeName = employees[0];
    defaultPrompts[0] = {
      label: `${employeeName}'s allocation details`,
      description: 'Check current and upcoming workload.',
      prompt: `What is ${employeeName}'s total allocation for ${currentMonth} and ${nextMonth}? Show hours allocated per project, FTE percentage, and remaining capacity.`
    };
  }

  // If we have projects, customize the second prompt
  if (projects.length > 0) {
    const projectName = projects[0];
    defaultPrompts[1] = {
      label: `Find staff for ${projectName}`,
      description: 'Find employees with capacity for this project.',
      prompt: `Which employees have availability to work on ${projectName} in ${currentMonthOnly} and the next 2 months? Show their current FTE, available hours, and any existing project commitments.`
    };
  }

  return defaultPrompts;
}

export default function AIChatPage() {
  const { user } = useAuth();
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<ConversationEntry[]>([]);
  const lastQueryTime = useRef<number>(0);

  const scrollRef = useRef<HTMLDivElement>(null);

  // Fetch manager's employees
  const { data: employees = [] } = useQuery({
    queryKey: ['employees', user?.id],
    queryFn: () => fetchEmployees({ managerId: user!.id }),
    enabled: !!user?.id
  });

  // Fetch manager's projects
  const { data: projects = [] } = useQuery({
    queryKey: ['projects', user?.id],
    queryFn: () => fetchProjects({ managerId: user!.id }),
    enabled: !!user?.id
  });

  // Auto-refresh AI knowledge base on page load
  useEffect(() => {
    if (user?.id && employees.length > 0) {
      // Trigger reindex once we have user data loaded
      const timer = setTimeout(() => {
        reindexMutation.mutate();
      }, 500);
      
      return () => clearTimeout(timer);
    }
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [user?.id, employees.length]);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: 'smooth' });
  }, [history]);

  const chatMutation = useMutation({
    mutationFn: (query: string) => {
      if (!user?.id) return Promise.reject(new Error('User not authenticated'));
      return chatWithAI({ query, manager_id: user.id, context_limit: 5 });
    },
    onSuccess: (response: ChatQueryResponse) => {
      appendMessage({
        id: crypto.randomUUID(),
        role: 'assistant',
        content: response.answer,
        createdAt: buildTimestamp()
      });
    },
    onError: (error: Error) => {
      const errorMsg = error.message.includes('502') 
        ? 'The AI service is experiencing high load or a timeout. Please wait a moment and try again, or try a simpler question.' 
        : error.message.includes('503')
        ? 'The AI service is not configured. Please check that the GOOGLE_API_KEY is set in the backend .env file.'
        : `Unable to complete the request: ${error.message}`;
      
      appendMessage({
        id: crypto.randomUUID(),
        role: 'system',
        content: `❌ ${errorMsg}`,
        createdAt: buildTimestamp()
      });
    }
  });

  const reindexMutation = useMutation({
    mutationFn: triggerReindex,
    onSuccess: (data) => {
      // Only show message if manually triggered (not on auto-load)
      if (history.length > 0) {
        appendMessage({
          id: crypto.randomUUID(),
          role: 'system',
          content: `✅ AI knowledge base refreshed successfully! ${data.message}`,
          createdAt: buildTimestamp()
        });
      }
    },
    onError: (error: Error) => {
      appendMessage({
        id: crypto.randomUUID(),
        role: 'system',
        content: `❌ Failed to refresh knowledge base: ${error.message}. Please try clicking "Refresh Data" button again.`,
        createdAt: buildTimestamp()
      });
    }
  });

  const appendMessage = useCallback((entry: ConversationEntry) => {
    setHistory((prev) => [...prev, entry]);
  }, []);

  const handleSubmit = useCallback(async (prompt: string) => {
    if (!prompt.trim()) return;
    
    // Rate limiting: prevent queries within 2 seconds of each other
    const now = Date.now();
    const timeSinceLastQuery = now - lastQueryTime.current;
    if (timeSinceLastQuery < 2000 && lastQueryTime.current > 0) {
      appendMessage({
        id: crypto.randomUUID(),
        role: 'system',
        content: '⏱️ Please wait a moment between queries to avoid rate limits.',
        createdAt: buildTimestamp()
      });
      return;
    }
    
    lastQueryTime.current = now;
    appendMessage({
      id: crypto.randomUUID(),
      role: 'user',
      content: prompt.trim(),
      createdAt: buildTimestamp()
    });
    chatMutation.mutate(prompt.trim());
  }, [appendMessage, chatMutation]);

  const presetPrompts = useMemo(() => {
    const employeeNames = employees.map(emp => emp.full_name);
    const projectNames = projects.map(proj => proj.name);
    return generatePresetPrompts(employeeNames, projectNames);
  }, [employees, projects]);

  const presetButtons = useMemo(
    () =>
      presetPrompts.map((preset) => (
        <PresetButton
          key={preset.label}
          label={preset.label}
          description={preset.description}
          icon={<Sparkles className="h-4 w-4" />}
          onSelect={() => {
            setInput(preset.prompt);
            handleSubmit(preset.prompt);
          }}
        />
      )),
    [presetPrompts, handleSubmit]
  );

  return (
    <div className="flex flex-col gap-4" style={{ height: 'calc(100vh - 8rem)' }}>
      <SectionHeader
          title="StaffAlloc AI Assistant"
          description="Ask specific questions about your employees' allocations, project staffing, and availability. Include dates for best results."
          action={
          <div className="flex items-center gap-2">
            <button
              type="button"
              onClick={() => reindexMutation.mutate()}
              disabled={reindexMutation.isPending}
              className="inline-flex items-center gap-2 rounded-full border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-semibold text-emerald-700 transition hover:bg-emerald-100 disabled:opacity-50"
              title="Refresh AI knowledge base with latest data"
            >
              {reindexMutation.isPending ? (
                <Loader2 className="h-3.5 w-3.5 animate-spin" />
              ) : (
                <Database className="h-3.5 w-3.5" />
              )}
              Refresh Data
            </button>
            <button
              type="button"
              onClick={() => setHistory([])}
              className="inline-flex items-center gap-2 rounded-full border border-slate-200 bg-white px-3 py-1 text-xs font-semibold text-slate-600 transition hover:border-blue-200 hover:text-blue-600"
            >
              <RefreshCw className="h-3.5 w-3.5" />
              Clear Chat
            </button>
          </div>
        }
      />

      <div className="flex-shrink-0">
        <Card>
        {reindexMutation.isPending && (
          <div className="mb-4 rounded-lg border border-emerald-200 bg-emerald-50 p-3 text-sm text-emerald-700">
            <div className="flex items-center gap-2">
              <Loader2 className="h-4 w-4 animate-spin" />
              <span>Refreshing AI knowledge base with your latest project and employee data...</span>
            </div>
          </div>
        )}
          <div className="grid gap-3 md:grid-cols-3">{presetButtons}</div>
        </Card>
      </div>

      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col flex-1 min-h-0">
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4">
          <div className="space-y-3">
            {history.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center text-sm text-slate-500 py-12">
                <Brain className="mb-3 h-10 w-10 text-blue-500" />
                <p className="font-semibold text-slate-700">Start a conversation with the StaffAlloc AI.</p>
                <p className="mt-1">Use the preset prompts or ask your own question about allocations.</p>
                <div className="mt-4 max-w-md rounded-lg border border-blue-100 bg-blue-50 p-3 text-xs text-blue-700">
                  <p className="font-semibold mb-1">💡 Tips for best results:</p>
                  <ul className="list-disc list-inside space-y-1 text-left">
                    <li>Include specific dates (e.g., "November 2025")</li>
                    <li>Use employee or project names from your data</li>
                    <li>If you get "not found", click <strong>Refresh Data</strong> button</li>
                  </ul>
                </div>
              </div>
            ) : (
              <AnimatePresence initial={false}>
                {history.map((message) => (
                  <motion.div
                    key={message.id}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    exit={{ opacity: 0, y: -8 }}
                  >
                    <ChatMessage role={message.role} content={message.content} timestamp={message.createdAt} />
                  </motion.div>
                ))}
              </AnimatePresence>
            )}
            {chatMutation.isPending && (
              <div className="flex items-center gap-2 text-xs text-slate-500 pb-4">
                <Loader2 className="h-4 w-4 animate-spin" />
                AI composing response…
              </div>
            )}
          </div>
        </div>
        <form
          className="flex-shrink-0 border-t border-slate-200 bg-slate-50 p-4"
          onSubmit={(event) => {
            event.preventDefault();
            handleSubmit(input);
            setInput('');
          }}
        >
          <div className="flex items-center gap-3">
            <input
              type="text"
              placeholder="Ask anything about staffing, utilization, or allocations…"
              value={input}
              onChange={(event) => setInput(event.target.value)}
              className="flex-1 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-700 transition focus:border-blue-400 focus:outline-none focus:ring-2 focus:ring-blue-100"
            />
              <button
                type="submit"
                disabled={chatMutation.isPending}
                className="inline-flex items-center gap-2 rounded-lg bg-blue-600 px-4 py-2 text-sm font-semibold text-white shadow-sm transition hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                {chatMutation.isPending ? (
                  <>
                    <Loader2 className="h-4 w-4 animate-spin" />
                    <span>Sending...</span>
                  </>
                ) : (
                  'Send'
                )}
              </button>
          </div>
        </form>
      </div>
    </div>
  );
}

