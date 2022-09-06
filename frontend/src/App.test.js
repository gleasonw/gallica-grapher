import React from 'react';
import { render, screen } from '@testing-library/react';
import fireEvent from '@testing-library/user-event';
import '@testing-library/jest-dom'
import App from './App';
import { server } from './mocks/server.js';

window.scrollTo = jest.fn();

beforeAll(() => server.listen());
afterEach(() => {
    server.resetHandlers()
    jest.resetAllMocks();
});
afterAll(() => {
    server.close()
    jest.clearAllMocks()
});

describe('The main application cycle for the Gallica Grapher.', () => {
    it('renders correctly', () => {
        render(<App />);
        expect(screen.getByText('Graphing Gallica')).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Information page button'})).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Home page button'})).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Scroll to examples'})).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Fetch and graph 📊'})).toBeInTheDocument();
    });
    it('displays the information page when the info button is clicked', () => {
        render(<App />);
        fireEvent.click(screen.getByRole('button', {name: 'Information page button'}));
        expect(screen.getByText('This is a graphing tool.')).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Home page button'})).toBeInTheDocument();
    });
    it('displays the home page when the home button is clicked', () => {
        render(<App />);
        fireEvent.click(screen.getByRole('button', {name: 'Information page button'}));
        fireEvent.click(screen.getByRole('button', {name: 'Home page button'}));
        expect(screen.getByText('Graphing Gallica')).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Information page button'})).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Home page button'})).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Scroll to examples'})).toBeInTheDocument();
        expect(screen.getByRole('button', {name: 'Fetch and graph 📊'})).toBeInTheDocument();
    });
});