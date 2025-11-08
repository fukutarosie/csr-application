import './globals.css'
import { ToastProvider } from './components/ToastProvider'

export const metadata = {
  title: 'CSR Application',
  description: 'Customer Service Request Management System',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>
        <ToastProvider>
          {children}
        </ToastProvider>
      </body>
    </html>
  )
}