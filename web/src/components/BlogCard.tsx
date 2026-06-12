import Link from "next/link";

interface BlogCardProps {
  slug: string;
  title: string;
  date: string;
  category: string;
  excerpt: string;
}

export default function BlogCard({
  slug,
  title,
  date,
  category,
  excerpt,
}: BlogCardProps) {
  return (
    <Link
      href={`/blog/${slug}`}
      className="block border border-gray-200 rounded-xl p-6 hover:border-brand-500 transition-colors"
    >
      <span className="text-xs text-brand-500 font-medium">
        {date} · {category}
      </span>
      <h3 className="text-xl font-semibold mt-1 mb-2">{title}</h3>
      <p className="text-gray-500 text-sm">{excerpt}</p>
    </Link>
  );
}
