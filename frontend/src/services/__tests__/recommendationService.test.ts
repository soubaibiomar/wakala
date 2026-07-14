import { describe, it, expect, vi, beforeEach } from 'vitest';
import { recommendationService } from '../recommendationService';

const mockApiPost = vi.fn();

vi.mock('../api', () => ({
  default: {
    post: (...args: unknown[]) => mockApiPost(...args),
    get: vi.fn(),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
}));

describe('recommendationService', () => {
  beforeEach(() => {
    mockApiPost.mockReset();
  });

  it('calls POST /recommendation/ with query', async () => {
    mockApiPost.mockResolvedValue({
      data: { items: [], total: 0, page: 1, page_size: 5, method: 'cold-start' },
    });

    await recommendationService.search({ query: 'SUV diesel' });

    expect(mockApiPost).toHaveBeenCalledWith('/recommendation/', {
      query: 'SUV diesel',
      filters: undefined,
      page: undefined,
      page_size: undefined,
    });
  });

  it('sends filters when provided', async () => {
    mockApiPost.mockResolvedValue({
      data: { items: [], total: 0, page: 1, page_size: 5, method: 'cold-start' },
    });

    await recommendationService.search({
      query: 'voiture',
      filters: { fuel_type: 'diesel', price_min: 10000 },
      page: 1,
      page_size: 10,
    });

    const callArgs = mockApiPost.mock.calls[0][1];
    expect(callArgs.filters).toBeDefined();
    expect(callArgs.filters.fuel_type).toBe('diesel');
    expect(callArgs.page).toBe(1);
    expect(callArgs.page_size).toBe(10);
  });

  it('returns proper response structure on success', async () => {
    const mockResponse = {
      items: [
        { vehicle_id: 'v1', match_score: 85.0, score_breakdown: { content: 0.9, collaborative: 0.3 } },
        { vehicle_id: 'v2', match_score: 70.0, score_breakdown: { content: 0.7, collaborative: 0.5 } },
      ],
      total: 2,
      page: 1,
      page_size: 5,
      method: 'hybrid',
    };
    mockApiPost.mockResolvedValue({ data: mockResponse });

    const result = await recommendationService.search({ query: 'test' });
    expect(result.items).toHaveLength(2);
    expect(result.method).toBe('hybrid');
    expect(result.items[0].match_score).toBe(85.0);
  });

  it('handles empty query gracefully', async () => {
    mockApiPost.mockResolvedValue({
      data: { items: [], total: 0, page: 1, page_size: 5, method: 'cold-start' },
    });

    const result = await recommendationService.search({ query: '' });
    expect(result.items).toEqual([]);
    expect(result.total).toBe(0);
  });
});
