"use client";

import { useState, useEffect, useRef } from 'react';
import { updateProjectApi, UpdateProjectPayload, Project } from '@/lib/api';

export type SaveStatus = 'idle' | 'saving' | 'saved' | 'error';

export function useAutoSave(
  projectId: string | undefined,
  payload: UpdateProjectPayload,
  debounceMs: number = 1000
) {
  const [saveStatus, setSaveStatus] = useState<SaveStatus>('idle');
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const isFirstRender = useRef(true);
  const timeoutRef = useRef<NodeJS.Timeout | null>(null);

  useEffect(() => {
    if (isFirstRender.current) {
      isFirstRender.current = false;
      return;
    }

    if (!projectId) return;

    setSaveStatus('saving');

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    timeoutRef.current = setTimeout(async () => {
      try {
        await updateProjectApi(projectId, payload);
        setSaveStatus('saved');
        setLastSaved(new Date());
      } catch (err) {
        console.error("Auto-save error:", err);
        setSaveStatus('error');
      }
    }, debounceMs);

    return () => {
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
  }, [projectId, JSON.stringify(payload), debounceMs]);

  return { saveStatus, lastSaved };
}
