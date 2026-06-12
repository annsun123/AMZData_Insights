import Link from "next/link";

export default function Layout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen flex flex-col bg-white">
      <nav className="border-b border-gray-200">
        <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between">
          <Link href="/" className="text-xl font-bold text-brand-900">
            AMZ Data
            <span className="text-sm font-normal text-gray-400 ml-2">
              Pet Intelligence
            </span>
          </Link>
          <div className="flex gap-6 text-sm font-medium">
            <Link href="/blog" className="text-gray-600 hover:text-brand-500">
              Blog
            </Link>
            <Link href="/tools" className="text-gray-600 hover:text-brand-500">
              Tools
            </Link>
          </div>
        </div>
      </nav>
      <main className="flex-1 max-w-5xl mx-auto px-4 py-8 w-full">
        {children}
      </main>
      <footer className="border-t border-gray-100 py-8 text-center text-sm text-gray-400">
        AMZ Data — Data insights for Amazon sellers
      </footer>
    </div>
  );
}
