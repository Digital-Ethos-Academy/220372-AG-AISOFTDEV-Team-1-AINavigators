import type { ReactNode } from 'react';

interface ChatMessageProps {
  role: 'user' | 'assistant' | 'system';
  content: ReactNode;
  timestamp?: string;
}

const toneClasses: Record<ChatMessageProps['role'], string> = {
  user: 'border-blue-200 bg-blue-50 text-blue-800',
  assistant: 'border-slate-200 bg-white text-slate-800',
  system: 'border-amber-200 bg-amber-50 text-amber-800'
};

// Simple markdown-like formatting for common patterns
function formatContent(content: string): ReactNode {
  // Split by lines for processing
  const lines = content.split('\n');
  const formatted: ReactNode[] = [];
  
  lines.forEach((line, idx) => {
    let processedLine = line;
    
    // Bold text: **text** or __text__
    processedLine = processedLine.replace(/\*\*(.+?)\*\*/g, '<strong>$1</strong>');
    processedLine = processedLine.replace(/__(.+?)__/g, '<strong>$1</strong>');
    
    // Bullet points
    if (line.trim().startsWith('* ') || line.trim().startsWith('- ')) {
      processedLine = processedLine.replace(/^[\s]*[*-]\s+/, '• ');
    }
    
    // Headers (### or ##)
    if (line.trim().startsWith('###')) {
      processedLine = `<div class="font-semibold mt-2">${line.replace(/^###\s*/, '')}</div>`;
    } else if (line.trim().startsWith('##')) {
      processedLine = `<div class="font-bold mt-2">${line.replace(/^##\s*/, '')}</div>`;
    }
    
    formatted.push(
      <span key={idx} dangerouslySetInnerHTML={{ __html: processedLine }} className="block" />
    );
  });
  
  return <>{formatted}</>;
}

export default function ChatMessage({ role, content, timestamp }: ChatMessageProps) {
  const formattedContent = typeof content === 'string' ? formatContent(content) : content;
  
  return (
    <div
      className={`flex flex-col gap-1 rounded-xl border px-4 py-3 text-sm shadow-sm ${toneClasses[role]}`}
    >
      <div className="flex items-center justify-between text-xs font-semibold uppercase tracking-wide">
        <span>{role === 'assistant' ? 'StaffAlloc AI' : role === 'user' ? 'You' : 'System'}</span>
        {timestamp && <time className="text-xs font-medium opacity-70">{timestamp}</time>}
      </div>
      <div className="leading-relaxed space-y-1">{formattedContent}</div>
    </div>
  );
}

