"use client";

import { useState, useEffect, useRef } from 'react';
import { updateProjectApi, UpdateProjectPayload } from '@/lib/api';

const getErrorMessage = (error: unknown): string => {
  return error instanceof Error ? error.message : 'An unexpected error occurred';
};

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

    if (timeoutRef.current) {
      clearTimeout(timeoutRef.current);
    }

    // Flip to 'saving' on the next tick rather than synchronously in the
    // effect body, then run the actual debounced save.
    const savingTimeout = setTimeout(() => setSaveStatus('saving'), 0);

    timeoutRef.current = setTimeout(async () => {
      try {
        await updateProjectApi(projectId, payload);
        setSaveStatus('saved');
        setLastSaved(new Date());
      } catch (error: unknown) {
        console.error("Auto-save error:", getErrorMessage(error));
        setSaveStatus('error');
      }
    }, debounceMs);

    return () => {
      clearTimeout(savingTimeout);
      if (timeoutRef.current) {
        clearTimeout(timeoutRef.current);
      }
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [projectId, JSON.stringify(payload), debounceMs]);

  return { saveStatus, lastSaved };
}
