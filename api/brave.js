export default async function handler(req, res) {
  // CORS headers
  res.setHeader('Access-Control-Allow-Origin', '*');
  res.setHeader('Access-Control-Allow-Methods', 'POST, OPTIONS');
  res.setHeader('Access-Control-Allow-Headers', 'Content-Type');
  
  if (req.method === 'OPTIONS') {
    return res.status(200).end();
  }

  if (req.method !== 'POST') {
    return res.status(405).json({ error: 'Method not allowed' });
  }

  const BRAVE_KEY = process.env.BRAVE_KEY || process.env.VITE_BRAVE_KEY;
  if (!BRAVE_KEY) {
    return res.status(500).json({ error: 'Brave API key not configured' });
  }

  try {
    const { query } = req.body;
    if (!query) {
      return res.status(400).json({ error: 'Query required' });
    }

    const url = `https://api.search.brave.com/res/v1/web/search?q=${encodeURIComponent(query)}&count=4`;
    const response = await fetch(url, {
      headers: {
        'Accept': 'application/json',
        'X-Subscription-Token': BRAVE_KEY,
      },
    });

    // Enhanced error handling: check response status
    if (!response.ok) {
      const statusCode = response.status;
      let errorType = 'UNKNOWN_ERROR';
      let errorMessage = 'Unknown error occurred';

      if (statusCode === 401) {
        errorType = 'UNAUTHORIZED';
        errorMessage = 'API key is invalid or expired';
      } else if (statusCode === 403) {
        errorType = 'FORBIDDEN';
        errorMessage = 'Access forbidden - check API key permissions';
      } else if (statusCode === 429) {
        errorType = 'RATE_LIMIT';
        errorMessage = 'Rate limit exceeded - too many requests';
      } else if (statusCode >= 500) {
        errorType = 'SERVER_ERROR';
        errorMessage = 'Brave API server error';
      } else if (statusCode >= 400) {
        errorType = 'CLIENT_ERROR';
        errorMessage = 'Bad request to Brave API';
      }

      return res.status(statusCode).json({
        error: errorType,
        message: errorMessage,
        statusCode
      });
    }

    const data = await response.json();
    return res.status(200).json(data);
  } catch (error) {
    return res.status(500).json({
      error: 'NETWORK_ERROR',
      message: error.message,
      details: 'Failed to connect to Brave API'
    });
  }
}
