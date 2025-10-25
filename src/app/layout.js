import './globals.css'

export const metadata = {
  title: 'CSR Application',
  description: 'Customer Service Request Management System',
}

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}