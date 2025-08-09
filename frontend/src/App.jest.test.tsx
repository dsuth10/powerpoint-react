import React from 'react';
import { render, screen } from '@testing-library/react';

test('renders a simple div', () => {
  render(<div>Hello Jest</div>);
  expect(screen.getByText('Hello Jest')).toBeInTheDocument();
}); 