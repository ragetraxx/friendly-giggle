// /api/proxy.js
export default async function handler(req, res) {
  const targetUrl = req.query.url;

  if (!targetUrl) {
    return res.status(400).json({ error: "Missing ?url=" });
  }

  try {
    const response = await fetch(targetUrl, {
      headers: {
        "User-Agent": req.headers["user-agent"] || "Mozilla/5.0",
      },
    });

    res.setHeader("Access-Control-Allow-Origin", "*");
    res.setHeader("Content-Type", response.headers.get("content-type") || "application/vnd.apple.mpegurl");

    const buffer = await response.arrayBuffer();
    res.send(Buffer.from(buffer));
  } catch (err) {
    res.status(500).json({ error: err.message });
  }
}
