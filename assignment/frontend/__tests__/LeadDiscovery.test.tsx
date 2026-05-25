import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { vi, describe, beforeEach, it, expect } from 'vitest';
import Page from '../app/page';

global.fetch = vi.fn();

describe('Lead Discovery - Happy Path Flow', () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it('completes the submit -> pending -> results flow successfully', async () => {

    (global.fetch as any)
      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          job_id: 'job-123',
          status: 'pending',
        }),
      })

      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          job_id: 'job-123',
          status: 'pending',
        }),
      })

      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          job_id: 'job-123',
          status: 'done',
        }),
      })

      .mockResolvedValueOnce({
        ok: true,
        json: async () => ({
          leads: [
            {
              id: 'lead-1',
              name: 'Rexplore Labs',
              category: 'Software Solutions',
              country: 'Malawi',
              headquarters_city: 'Lilongwe',
              fit_score: '0.95',
              justification:
                'Strong fit for enterprise software solutions.',
              rank: 1,
            },
          ],
        }),
      });

    render(<Page />);

    fireEvent.change(
      screen.getByLabelText(/Business Description/i),
      {
        target: {
          value: 'We produce packaged snacks',
        },
      }
    );

    fireEvent.change(
      screen.getByRole('combobox'),
      {
        target: { value: 'KE' },
      }
    );

    fireEvent.click(
      screen.getByRole('button', {
        name: /Discover Leads/i,
      })
    );

    expect(
      await screen.findByText(/Mining Data/i)
    ).toBeInTheDocument();

    await waitFor(
      async () => {
        expect(
          await screen.findByText(/Rexplore Labs/i)
        ).toBeInTheDocument();
      },
      { timeout: 6000 }
    );

    expect(
      screen.getByText(
        /Strong fit for enterprise software solutions/i
      )
    ).toBeInTheDocument();

    expect(
      screen.getByText(/95%/)
    ).toBeInTheDocument();

    expect(global.fetch).toHaveBeenCalledTimes(4);
  }, 10000);
});