import praw
import pandas as pd
from datetime import datetime
from pipeline.config import (
    REDDIT_CLIENT_ID, REDDIT_CLIENT_SECRET, REDDIT_USER_AGENT
)

PET_SUBREDDITS = ["dogs", "cats", "Pets", "DogFood", "CatAdvice", "puppy101"]

class RedditFetcher:
    """Fetch Reddit discussions for consumer signal detection."""

    def __init__(self):
        self.reddit = praw.Reddit(
            client_id=REDDIT_CLIENT_ID,
            client_secret=REDDIT_CLIENT_SECRET,
            user_agent=REDDIT_USER_AGENT,
        )

    def search_pet_discussions(self, keyword: str,
                                subreddits: list[str] | None = None,
                                limit: int = 100,
                                time_filter: str = "year") -> pd.DataFrame:
        """Search pet subreddits for keyword mentions. Returns DataFrame with
        title, score, num_comments, created_utc, subreddit, and url."""
        if subreddits is None:
            subreddits = PET_SUBREDDITS

        subreddit_str = "+".join(subreddits)
        posts = []

        for submission in self.reddit.subreddit(subreddit_str).search(
            keyword, sort="relevance", time_filter=time_filter, limit=limit
        ):
            posts.append({
                "title": submission.title,
                "selftext": submission.selftext[:500],
                "score": submission.score,
                "num_comments": submission.num_comments,
                "created_utc": datetime.utcfromtimestamp(submission.created_utc),
                "subreddit": str(submission.subreddit),
                "url": submission.url,
                "keyword": keyword,
            })

        return pd.DataFrame(posts)

    def get_signal_strength(self, keyword: str,
                            time_filter: str = "year") -> dict:
        """Calculate signal strength from Reddit discussion volume and engagement."""
        subreddits = ["dogs", "Pets", "CatAdvice", "puppy101"]
        subreddit_str = "+".join(subreddits)
        posts = []

        for submission in self.reddit.subreddit(subreddit_str).search(
            keyword, sort="relevance", time_filter=time_filter, limit=200
        ):
            posts.append({
                "score": submission.score,
                "num_comments": submission.num_comments,
            })

        if not posts:
            return {"keyword": keyword, "total_posts": 0, "avg_score": 0,
                    "avg_comments": 0, "signal_strength": "none"}

        df = pd.DataFrame(posts)
        avg_score = df["score"].mean()
        avg_comments = df["num_comments"].mean()
        total = len(posts)

        # Heuristic signal strength
        if total > 50 and avg_score > 100:
            strength = "strong"
        elif total > 20 and avg_score > 30:
            strength = "moderate"
        elif total > 0:
            strength = "weak"
        else:
            strength = "none"

        return {
            "keyword": keyword,
            "total_posts": total,
            "avg_score": round(avg_score, 1),
            "avg_comments": round(avg_comments, 1),
            "signal_strength": strength,
        }
