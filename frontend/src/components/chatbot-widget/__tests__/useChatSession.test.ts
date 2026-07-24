import { describe, it, expect, vi, beforeEach, afterEach } from 'vitest';
import { renderHook, act, waitFor } from '@testing-library/react';
import { useChatSession } from '../useChatSession';

const mockStreamMessage = vi.fn();

vi.mock('../../services/chatbotService', () => ({
  chatbotService: {
    streamMessage: (...args: unknown[]) => mockStreamMessage(...args),
  },
}));

describe('useChatSession', () => {
  beforeEach(() => {
    sessionStorage.clear();
    mockStreamMessage.mockReset();
  });

  it('starts with empty messages', () => {
    const { result } = renderHook(() => useChatSession());
    expect(result.current.messages).toEqual([]);
    expect(result.current.isTyping).toBe(false);
    expect(result.current.error).toBeNull();
  });

  it('adds user message when sending', async () => {
    mockStreamMessage.mockImplementation(async (msg, hist, onChunk) => {
      onChunk('Reponse test');
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
    mockStreamMessage.mockRejectedValue(new Error('Network error'));

    const { result } = renderHook(() => useChatSession());
    await act(async () => {
      await result.current.sendMessage('Test');
    });

    expect(result.current.messages.length).toBe(2);
    expect(result.current.messages[1].content).toContain('Désolé');
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
    mockStreamMessage.mockReturnValue(apiPromise);

    const { result } = renderHook(() => useChatSession());

    let sendPromise: Promise<void>;
    act(() => {
      sendPromise = result.current.sendMessage('Test');
    });

    expect(result.current.isTyping).toBe(true);

    await act(async () => {
      resolvePromise!();
      await apiPromise;
      await sendPromise;
    });

    expect(result.current.isTyping).toBe(false);
  });
});
