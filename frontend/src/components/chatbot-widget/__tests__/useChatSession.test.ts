import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChatSession } from '../useChatSession';

const mockApiPost = vi.fn();

vi.mock('../../../services/api', () => ({
  default: {
    post: (...args: unknown[]) => mockApiPost(...args),
    get: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
}));

describe('useChatSession', () => {
  beforeEach(() => {
    sessionStorage.clear();
    mockApiPost.mockReset();
  });

  it('starts with empty messages', () => {
    const { result } = renderHook(() => useChatSession());
    expect(result.current.messages).toEqual([]);
    expect(result.current.isTyping).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('adds user message when sending', async () => {
    mockApiPost.mockResolvedValue({
      data: { reply: 'Reponse test', sources: [], session_id: 'test' },
    });

    const { result } = renderHook(() => useChatSession());
    await act(async () => {
      await result.current.sendMessage('Bonjour');
    });

    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[0].role).toBe('user');
    expect(result.current.messages[0].content).toBe('Bonjour');
    expect(result.current.messages[1].role).toBe('assistant');
  });

  it('ignores empty messages', async () => {
    const { result } = renderHook(() => useChatSession());
    await act(async () => {
      await result.current.sendMessage('   ');
    });

    expect(result.current.messages.length).toBe(0);
  });

  it('handles API error gracefully', async () => {
    mockApiPost.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useChatSession());
    await act(async () => {
      await result.current.sendMessage('Test');
    });

    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[1].content).toContain('Desole');
    expect(result.current.error).toBeTruthy();
  });

  it('clearHistory resets messages and creates new session', () => {
    const { result } = renderHook(() => useChatSession());
    act(() => {
      result.current.clearHistory();
    });

    expect(result.current.messages).toEqual([]);
    expect(result.current.error).toBeNull();
  });

  it('manages typing state', async () => {
    let resolvePromise: (v: unknown) => void;
    const apiPromise = new Promise((resolve) => {
      resolvePromise = resolve;
    });
    mockApiPost.mockReturnValue(apiPromise);

    const { result } = renderHook(() => useChatSession());

    act(() => {
      result.current.sendMessage('Test');
    });

    expect(result.current.isTyping).toBe(true);

    await act(async () => {
      resolvePromise!({
        data: { reply: 'Reponse', sources: [], session_id: 'test' },
      });
      await apiPromise;
    });

    expect(result.current.isTyping).toBe(false);
  });
});
