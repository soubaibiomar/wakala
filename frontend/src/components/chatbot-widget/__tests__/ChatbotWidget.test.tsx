import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { MemoryRouter } from 'react-router-dom';
import ChatbotWidget from '../ChatbotWidget';

Element.prototype.scrollIntoView = vi.fn() as unknown as () => void;

vi.mock('../../../services/api', () => ({
  default: {
    get: vi.fn(),
    post: vi.fn().mockResolvedValue({ data: { reply: 'Test reply', sources: [] } }),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
}));

vi.mock('../chatbot.module.css', () => ({ default: {} }));


describe('ChatbotWidget', () => {
  it('renders the trigger button', () => {
    render(
      <MemoryRouter>
        <ChatbotWidget />
      </MemoryRouter>
    );

    const trigger = screen.queryByRole('button');
    expect(trigger).toBeTruthy();
  });

  it('opens the chat window on trigger click', () => {
    render(
      <MemoryRouter>
        <ChatbotWidget />
      </MemoryRouter>
    );

    const trigger = screen.getAllByRole('button')[0];
    fireEvent.click(trigger);

    expect(screen.queryAllByText(/Assistant Wakala/i).length).toBeGreaterThanOrEqual(1);
  });
});
