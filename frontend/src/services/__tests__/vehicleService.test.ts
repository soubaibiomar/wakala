import { describe, it, expect, vi, beforeEach } from 'vitest';
import { vehicleService } from '../vehicleService';

const mockApiGet = vi.fn();
const mockApiPost = vi.fn();
const mockApiDelete = vi.fn();

vi.mock('../api', () => ({
  default: {
    get: (...args: unknown[]) => mockApiGet(...args),
    post: (...args: unknown[]) => mockApiPost(...args),
    delete: (...args: unknown[]) => mockApiDelete(...args),
    interceptors: { request: { use: vi.fn() }, response: { use: vi.fn() } },
  },
}));

describe('vehicleService', () => {
  beforeEach(() => {
    mockApiGet.mockReset();
    mockApiPost.mockReset();
    mockApiDelete.mockReset();
  });

  it('calls correct endpoint for getVehicles', async () => {
    mockApiGet.mockResolvedValue({
      data: { items: [], total: 0, page: 1, page_size: 12, pages: 0 },
    });

    await vehicleService.getVehicles({ brand: 'Renault' });

    expect(mockApiGet).toHaveBeenCalledWith('/vehicles/', expect.objectContaining({
      params: expect.objectContaining({ brand: 'Renault' }),
    }));
  });

  it('includes pagination params', async () => {
    mockApiGet.mockResolvedValue({
      data: { items: [], total: 0, page: 2, page_size: 6, pages: 0 },
    });

    await vehicleService.getVehicles({ page: 2, page_size: 6 });

    expect(mockApiGet).toHaveBeenCalledWith('/vehicles/', expect.objectContaining({
      params: expect.objectContaining({ page: 2, page_size: 6 }),
    }));
  });

  it('filters out empty params', async () => {
    mockApiGet.mockResolvedValue({
      data: { items: [], total: 0, page: 1, page_size: 12, pages: 0 },
    });

    await vehicleService.getVehicles({ brand: '', fuel_type: '' as never });

    expect(mockApiGet).toHaveBeenCalledWith('/vehicles/', expect.objectContaining({
      params: expect.not.objectContaining({ brand: '' }),
    }));
  });

  it('fetches vehicle by id', async () => {
    mockApiGet.mockResolvedValue({
      data: { id: 'v1', brand: 'Renault', model: 'Clio' },
    });

    const result = await vehicleService.getVehicleById('v1');
    expect(mockApiGet).toHaveBeenCalledWith('/vehicles/v1');
    expect(result.brand).toBe('Renault');
  });

  it('creates a vehicle', async () => {
    mockApiPost.mockResolvedValue({
      data: { id: 'new-id', brand: 'Peugeot', model: '3008' },
    });

    const result = await vehicleService.createVehicle({
      brand: 'Peugeot', model: '3008', year: 2022,
      mileage: 10000, fuel_type: 'diesel', body_type: 'suv',
      transmission: 'automatique', price: 30000, doors: 5,
      seats: 5, city: 'Rabat',
    });

    expect(mockApiPost).toHaveBeenCalledWith('/vehicles/', expect.any(Object));
    expect(result.id).toBe('new-id');
  });

  it('deletes a vehicle', async () => {
    mockApiDelete.mockResolvedValue({ data: null });

    await vehicleService.deleteVehicle('v1');
    expect(mockApiDelete).toHaveBeenCalledWith('/vehicles/v1');
  });
});
