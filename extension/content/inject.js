(function () {
  "use strict";

  const API_BASE = "https://amzdata.com/api/trends";
  const ASIN_REGEX = /\/dp\/([A-Z0-9]{10})/;

  function getASIN() {
    const match = window.location.pathname.match(ASIN_REGEX);
    return match ? match[1] : null;
  }

  function getCategoryFromDOM() {
    const breadcrumbs = document.querySelectorAll(
      "#wayfinding-breadcrumbs_feature_div a, .a-breadcrumb a"
    );
    for (const el of breadcrumbs) {
      const text = el.textContent.toLowerCase().trim();
      if (
        ["pet supplies", "dogs", "cats", "pet food", "pet toys"].includes(
          text
        )
      ) {
        return text;
      }
    }
    return null;
  }

  function getProductTitle() {
    const titleEl = document.querySelector("#productTitle");
    return titleEl ? titleEl.textContent.trim() : "";
  }

  function injectTrendBadge(score) {
    const existing = document.getElementById("amzdata-trend-badge");
    if (existing) existing.remove();

    const color =
      score >= 70 ? "#16a34a" : score >= 40 ? "#ca8a04" : "#dc2626";
    const bg =
      score >= 70 ? "#f0fdf4" : score >= 40 ? "#fefce8" : "#fef2f2";

    const badge = document.createElement("div");
    badge.id = "amzdata-trend-badge";
    badge.style.cssText = `
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 12px; border-radius: 8px;
      background: ${bg}; border: 1px solid ${color};
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      margin-left: 12px; cursor: pointer;
    `;
    badge.innerHTML = `
      <span style="font-weight:700; font-size:16px; color:${color}">TrendScore</span>
      <span style="font-weight:700; font-size:18px; color:${color}">${score}/100</span>
    `;

    badge.addEventListener("click", () => {
      chrome.runtime.sendMessage({ action: "openSidePanel" });
    });

    const titleEl = document.querySelector("#productTitle");
    if (titleEl && titleEl.parentElement) {
      titleEl.parentElement.style.display = "flex";
      titleEl.parentElement.style.alignItems = "center";
      titleEl.parentElement.style.flexWrap = "wrap";
      titleEl.after(badge);
    }
  }

  function injectNoDataBadge() {
    const existing = document.getElementById("amzdata-trend-badge");
    if (existing) existing.remove();

    const badge = document.createElement("div");
    badge.id = "amzdata-trend-badge";
    badge.style.cssText = `
      display: inline-flex; align-items: center; gap: 6px;
      padding: 6px 12px; border-radius: 8px;
      background: #f9fafb; border: 1px solid #d1d5db;
      font-family: -apple-system, BlinkMacSystemFont, sans-serif;
      margin-left: 12px;
    `;
    badge.innerHTML = `
      <span style="font-weight:600; font-size:14px; color:#6b7280">TrendScore not yet available for this product</span>
    `;

    const titleEl = document.querySelector("#productTitle");
    if (titleEl && titleEl.parentElement) {
      titleEl.parentElement.style.display = "flex";
      titleEl.parentElement.style.alignItems = "center";
      titleEl.after(badge);
    }
  }

  async function fetchTrendScore(keyword) {
    try {
      const res = await fetch(
        `${API_BASE}?keyword=${encodeURIComponent(keyword)}`
      );
      if (!res.ok) return null;
      const data = await res.json();
      if (data.scores && data.scores.length > 0) {
        return data.scores[0].trend_score;
      }
      return null;
    } catch {
      return null;
    }
  }

  async function main() {
    const category = getCategoryFromDOM();
    if (!category) return;

    const asin = getASIN();
    if (!asin) return;

    const title = getProductTitle();
    if (!title) return;

    const keyword = title.split(" ").slice(0, 4).join(" ");

    const score = await fetchTrendScore(keyword);
    if (score !== null) {
      injectTrendBadge(score);
    } else {
      injectNoDataBadge();
    }
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", main);
  } else {
    main();
  }
})();
