import React from 'react';
import { RouterProvider } from 'react-router';
import { router } from './routes';
import { FleetProvider } from './state/store';
import { Toaster } from './components/ui/sonner';

export default function App() {
  return (
    <FleetProvider>
      <RouterProvider router={router} />
      <Toaster position="top-right" richColors />
    </FleetProvider>
  );
}