import BlogCard from "@/components/BlogCard";

const posts = [
  {
    slug: "pet-supplies-landscape",
    title: "Pet Supplies Market Landscape: Where the Growth Is",
    date: "June 2026",
    category: "Deep Dive",
    excerpt:
      "We analyzed 20+ pet sub-categories across search trends, BSR momentum, and Reddit discussion volume. Here are the 5 highest-signal opportunities.",
  },
];

export default function BlogPage() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Research & Analysis</h1>
      <p className="text-gray-500">
        Data-driven reports on Amazon Pet Supplies trends.
      </p>
      <div className="space-y-4 mt-8">
        {posts.map((post) => (
          <BlogCard key={post.slug} {...post} />
        ))}
      </div>
    </div>
  );
}
