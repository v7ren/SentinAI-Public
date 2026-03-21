import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'SecureBank - Online Banking',
  description: 'SecureBank - Your trusted online banking partner',
}

export default function RootLayout({
  children,
}: {
  children: React.ReactNode
}) {
  return (
    <html lang="en">
      <body>{children}</body>
    </html>
  )
}
