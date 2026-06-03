import React from 'react';
import { RouterProvider } from 'react-router';
import { router } from './routes';
import { FleetProvider } from './state/store';
import { Toaster } from './components/ui/sonner';
import { ErrorBoundary } from './components/ErrorBoundary';

export default function App() {
  return (
    <ErrorBoundary>
      <FleetProvider>
        <RouterProvider router={router} />
        <Toaster position="top-right" richColors />
      </FleetProvider>
    </ErrorBoundary>
  );
}