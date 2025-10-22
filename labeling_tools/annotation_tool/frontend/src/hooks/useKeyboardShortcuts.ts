import { useEffect, useCallback } from 'react';
import { KeyboardShortcuts } from '../types';

export const useKeyboardShortcuts = (shortcuts: KeyboardShortcuts, enabled = true) => {
  const handleKeyDown = useCallback((event: KeyboardEvent) => {
    if (!enabled) return;

    // Don't trigger shortcuts when typing in input fields
    if (event.target instanceof HTMLInputElement ||
        event.target instanceof HTMLTextAreaElement) {
      return;
    }

    const key = event.key.toLowerCase();
    const ctrlOrCmd = event.ctrlKey || event.metaKey;
    const shift = event.shiftKey;
    const alt = event.altKey;

    // Create shortcut string
    let shortcutKey = '';
    if (ctrlOrCmd) shortcutKey += 'cmd+';
    if (shift) shortcutKey += 'shift+';
    if (alt) shortcutKey += 'alt+';
    shortcutKey += key;

    // Also try without modifiers
    const simpleKey = key;

    if (shortcuts[shortcutKey]) {
      event.preventDefault();
      shortcuts[shortcutKey]();
    } else if (shortcuts[simpleKey] && !ctrlOrCmd && !shift && !alt) {
      event.preventDefault();
      shortcuts[simpleKey]();
    }
  }, [shortcuts, enabled]);

  useEffect(() => {
    if (enabled) {
      window.addEventListener('keydown', handleKeyDown);
      return () => window.removeEventListener('keydown', handleKeyDown);
    }
  }, [handleKeyDown, enabled]);
};