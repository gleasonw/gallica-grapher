import React from 'react';
import { render, screen } from '@testing-library/react';
import fireEvent from '@testing-library/user-event';
import '@testing-library/jest-dom'
import Input from './Input';
import { server } from '../mocks/server.js';

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

describe('The component where the user inputs their search information.', () => {
   it('displays the mocked number of continuous papers', async () => {
         render(<Input />);
         expect(await screen.findByText('')).toBeInTheDocument();
    });
});