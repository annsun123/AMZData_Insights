import { notFound } from "next/navigation";
import PetSuppliesLandscape from "@/content/blog/pet-supplies-landscape.mdx";

const posts: Record<
  string,
  { component: React.ComponentType; title: string; date: string }
> = {
  "pet-supplies-landscape": {
    component: PetSuppliesLandscape,
    title: "Pet Supplies Market Landscape: Where the Growth Is",
    date: "June 12, 2026",
  },
};

export function generateStaticParams() {
  return Object.keys(posts).map((slug) => ({ slug }));
}

export default function BlogPost({
  params,
}: {
  params: { slug: string };
}) {
  const post = posts[params.slug];
  if (!post) notFound();

  const Content = post.component;

  return (
    <article className="max-w-3xl mx-auto">
      <header className="mb-8">
        <span className="text-sm text-gray-400">{post.date}</span>
        <h1 className="text-3xl font-bold mt-1">{post.title}</h1>
      </header>
      <div className="prose prose-gray max-w-none">
        <Content />
      </div>
    </article>
  );
}
