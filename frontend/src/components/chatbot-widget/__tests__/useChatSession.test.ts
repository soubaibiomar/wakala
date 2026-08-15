import { describe, it, expect, vi, beforeEach } from 'vitest';
import { renderHook, act } from '@testing-library/react';
import { useChatSession } from '../useChatSession';

const { mockStreamMessage, mockGetChatHistory } = vi.hoisted(() => ({
  mockStreamMessage: vi.fn(),
  mockGetChatHistory: vi.fn().mockResolvedValue([]),
}));

vi.mock('../../../services/chatbotService', () => ({
  chatbotService: {
    streamMessage: mockStreamMessage,
    getChatHistory: mockGetChatHistory,
  },
}));

describe('useChatSession', () => {
  beforeEach(() => {
    localStorage.clear();
    sessionStorage.clear();
    mockStreamMessage.mockReset();
    mockGetChatHistory.mockReset().mockResolvedValue([]);
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
    mockStreamMessage.mockRejectedValueOnce(new Error('Network error'));

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
    let resolveStream: () => void = () => {};
    mockStreamMessage.mockImplementation(
      () =>
        new Promise<void>((resolve) => {
          resolveStream = resolve;
        })
    );

    const { result } = renderHook(() => useChatSession());

    let sendPromise: Promise<void> | undefined;
    act(() => {
      sendPromise = result.current.sendMessage('Test');
    });

    expect(result.current.isTyping).toBe(true);

    await act(async () => {
      resolveStream();
      if (sendPromise) await sendPromise;
    });

    expect(result.current.isTyping).toBe(false);
  });
});
