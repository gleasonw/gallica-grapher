import React from 'react';
import { render, screen } from '@testing-library/react';
import '@testing-library/jest-dom'
import App from './App';

describe('The main application cycle for the Gallica Grapher.', () => {
    it('renders correctly', () => {
        render(<App />);
        expect(screen.getByText('Graphing Gallica')).toBeInTheDocument();
    });

});