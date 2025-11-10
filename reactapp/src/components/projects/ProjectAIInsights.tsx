import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { useMutation } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Brain, Loader2, RefreshCw, Sparkles } from 'lucide-react';
import dayjs from 'dayjs';

import { chatWithAI } from '../../api/ai';
import type {
  ChatQueryResponse,
  LCAT,
  Role
} from '../../types/api';
import { Card } from '../common';
import { ChatMessage, PresetButton } from '../ai';
import { useAuth } from '../../context/AuthContext';

interface ConversationEntry {
  id: string;
  role: 'user' | 'assistant' | 'system';
  content: string;
  createdAt: string;
}

interface ProjectAIInsightsProps {
  projectId: number;
  roles: Role[];
  lcats: LCAT[];
}

function buildTimestamp() {
  return dayjs().format('MMM D, YYYY • h:mm A');
}

export default function ProjectAIInsights({ projectId }: ProjectAIInsightsProps) {
  const { user } = useAuth();
  const [input, setInput] = useState('');
  const [history, setHistory] = useState<ConversationEntry[]>([]);
  const lastQueryTime = useRef<number>(0);

  const scrollRef = useRef<HTMLDivElement>(null);

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

  const PRESET_PROMPTS = useMemo(() => {
    const currentMonth = dayjs().format('MMMM YYYY');
    const nextMonth = dayjs().add(1, 'month').format('MMMM YYYY');
    const twoMonthsOut = dayjs().add(2, 'months').format('MMMM YYYY');
    
    return [
      {
        label: `Which employees have capacity in ${nextMonth}?`,
        description: 'Find team members available for new work.',
        prompt: `Which employees have less than 80% FTE allocation in ${nextMonth}? List their names, current allocations, and available hours.`
      },
      {
        label: `Show current team workload`,
        description: 'See who is busy and who has capacity.',
        prompt: `Show me all employees and their FTE percentages for ${currentMonth}. Highlight anyone over 100% or under 50%.`
      },
      {
        label: `Who can take on more hours?`,
        description: 'Find employees with availability.',
        prompt: `Which employees have capacity to take on additional hours in ${nextMonth} and ${twoMonthsOut}? Show their current FTE and available hours per month.`
      }
    ];
  }, []);

  const presetButtons = useMemo(
    () =>
      PRESET_PROMPTS.map((preset) => (
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
    [PRESET_PROMPTS, handleSubmit]
  );

  return (
    <div className="space-y-4">
      <Card>
        <div className="mb-3 flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-700">Quick Availability Queries</h3>
          <button
            type="button"
            onClick={() => setHistory([])}
            className="inline-flex items-center gap-1.5 rounded-full border border-slate-200 bg-white px-2.5 py-1 text-xs font-semibold text-slate-600 transition hover:border-blue-200 hover:text-blue-600"
          >
            <RefreshCw className="h-3 w-3" />
            Clear
          </button>
        </div>
        <div className="grid gap-2 md:grid-cols-3">{presetButtons}</div>
      </Card>

      <div className="rounded-2xl border border-slate-200 bg-white shadow-sm flex flex-col min-h-0" style={{ height: '500px' }}>
        <div ref={scrollRef} className="flex-1 overflow-y-auto px-6 py-4">
          <div className="space-y-3">
            {history.length === 0 ? (
              <div className="flex flex-col items-center justify-center text-center text-sm text-slate-500 py-12">
                <Brain className="mb-3 h-10 w-10 text-blue-500" />
                <p className="font-semibold text-slate-700">Ask about employee availability</p>
                <p className="mt-1">Example: "Who is free to work 200 hours from March 2026 to October 2026?"</p>
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
              placeholder="Ask about employee availability for this project..."
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

