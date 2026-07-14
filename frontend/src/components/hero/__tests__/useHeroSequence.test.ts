import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useHeroSequence } from '../useHeroSequence';

describe('useHeroSequence', () => {
  beforeEach(() => {
    vi.useFakeTimers();
  });

  afterEach(() => {
    vi.useRealTimers();
  });

  it('starts with correct initial state', () => {
    const { result } = renderHook(() => useHeroSequence());
    expect(result.current.flashState).toBe('off');
    expect(result.current.plateState).toBe('plate');
    expect(result.current.isInteractive).toBe(false);
    expect(result.current.isApproaching).toBe(true);
  });

  it('transitions to flash1 after 2450ms', () => {
    const { result } = renderHook(() => useHeroSequence());
    act(() => {
      vi.advanceTimersByTime(2500);
    });
    expect(result.current.flashState).toBe('flash1');
  });

  it('transitions to on after 3200ms', () => {
    const { result } = renderHook(() => useHeroSequence());
    act(() => {
      vi.advanceTimersByTime(3300);
    });
    expect(result.current.flashState).toBe('on');
  });

  it('transitions plate to expanded at 3900ms', () => {
    const { result } = renderHook(() => useHeroSequence());
    act(() => {
      vi.advanceTimersByTime(4000);
    });
    expect(result.current.plateState).toBe('expanded');
    expect(result.current.isInteractive).toBe(true);
  });

  it('cleans up timers on unmount', () => {
    const { result, unmount } = renderHook(() => useHeroSequence());
    const spy = vi.spyOn(global, 'clearTimeout');
    unmount();
    expect(spy).toHaveBeenCalled();
  });
});
