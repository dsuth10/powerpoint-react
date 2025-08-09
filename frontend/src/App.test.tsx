import { render, screen } from '@testing-library/react';
import React from 'react';

describe('Sanity', () => {
  it('renders a simple div', () => {
    render(<div>Hello Test</div>);
    expect(screen.getByText('Hello Test')).toBeInTheDocument();
  });
}); 