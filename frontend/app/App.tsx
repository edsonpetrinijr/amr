import React from 'react';
import { RouterProvider } from 'react-router';
import { router } from './routes';
import { FleetProvider } from './state/store';

export default function App() {
  return (
    <FleetProvider>
      <RouterProvider router={router} />
    </FleetProvider>
  );
}