const API_BASE = "https://amzdata.com/api/trends";

function getActiveTabAmazonURL() {
  return new Promise((resolve) => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      if (
        tabs.length > 0 &&
        tabs[0].url &&
        tabs[0].url.includes("amazon.com")
      ) {
        resolve(tabs[0].url);
      } else {
        resolve(null);
      }
    });
  });
}

function extractKeywordFromURL(url) {
  const asinMatch = url.match(/\/dp\/([A-Z0-9]{10})/);
  if (asinMatch) {
    return { asin: asinMatch[1], keyword: null };
  }
  return null;
}

async function fetchAndDisplay() {
  const url = await getActiveTabAmazonURL();
  if (!url) {
    document.getElementById("product-info").innerHTML =
      '<p class="placeholder">⚠️ Open an Amazon product page to see trend signals.</p>';
    return;
  }

  const info = extractKeywordFromURL(url);
  if (!info) {
    document.getElementById("product-info").innerHTML =
      '<p class="placeholder">⚠️ Navigate to a product detail page.</p>';
    return;
  }

  document.getElementById("product-info").style.display = "none";
  document.getElementById("signals").style.display = "block";

  try {
    const res = await fetch(`${API_BASE}?keyword=pet`);
    if (!res.ok) throw new Error("API error");
    const data = await res.json();

    if (data.scores && data.scores.length > 0) {
      const top = data.scores[0];
      renderTrendScore(top);
    }
  } catch (err) {
    document.getElementById("trendscore-big").textContent = "Unavailable";
    console.error("AMZ Data fetch error:", err);
  }
}

function renderTrendScore(score) {
  const el = document.getElementById("trendscore-big");
  const color =
    score.trend_score >= 70
      ? "#16a34a"
      : score.trend_score >= 40
        ? "#ca8a04"
        : "#dc2626";
  el.style.color = color;
  el.style.borderColor = color;
  el.textContent = `${score.trend_score}/100`;

  const grid = document.getElementById("signal-grid");
  grid.innerHTML = "";

  const labels = {
    google_trends: "Google Trends",
    reddit_signal: "Reddit Signal",
    bsr_momentum: "BSR Momentum",
    velocity: "Velocity",
  };

  for (const [key, label] of Object.entries(labels)) {
    const value = score.components[key] || 0;
    const barColor =
      value >= 70 ? "#16a34a" : value >= 40 ? "#ca8a04" : "#dc2626";

    grid.innerHTML += `
      <div class="signal-item">
        <span class="signal-label">${label}</span>
        <div class="signal-bar-bg">
          <div class="signal-bar" style="width:${value}%;background:${barColor}"></div>
        </div>
        <span class="signal-value">${value}</span>
      </div>
    `;
  }

  document.getElementById("category-context").innerHTML = `
    <div class="context-card">
      <strong>Data Quality:</strong> ${score.data_quality}<br>
      <strong>Keyword:</strong> ${score.keyword}
    </div>
  `;
}

document.addEventListener("DOMContentLoaded", fetchAndDisplay);
