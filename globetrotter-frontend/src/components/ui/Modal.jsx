import { X } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useEffect } from 'react';

export const Modal = ({ isOpen, onClose, title, children }) => {
  useEffect(() => {
    if (isOpen) document.body.style.overflow = 'hidden';
    else document.body.style.overflow = 'unset';
    return () => { document.body.style.overflow = 'unset'; };
  }, [isOpen]);

  if (!isOpen) return null;

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/50 backdrop-blur-sm animate-in fade-in duration-200">
      <div className="bg-surface w-full max-w-lg rounded-2xl shadow-lg border border-border-default overflow-hidden flex flex-col max-h-[90vh] animate-in zoom-in-95 duration-200">
        
        <div className="flex justify-between items-center p-5 border-b border-border-subtle bg-surface">
          <h3 className="font-manrope text-xl font-semibold text-text-primary">{title}</h3>
          <button 
            onClick={onClose} 
            className="p-1.5 text-text-muted hover:text-text-primary rounded-full hover:bg-surface-hover transition-colors"
          >
            <X size={20} />
          </button>
        </div>
        
        <div className="p-5 overflow-y-auto">
          {children}
        </div>
      </div>
    </div>
  );
};