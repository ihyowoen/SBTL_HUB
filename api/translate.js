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

  try {
    const { text, sourceLang, targetLang } = req.body;
    if (!text || !targetLang) {
      return res.status(400).json({ error: 'text and targetLang are required' });
    }

    const langPair = `${sourceLang || 'auto'}|${targetLang}`;
    const url = `https://api.mymemory.translated.net/get?q=${encodeURIComponent(text)}&langpair=${encodeURIComponent(langPair)}`;

    const response = await fetch(url, {
      headers: { 'Accept': 'application/json' },
    });

    const data = await response.json();

    if (data.responseStatus === 200 && data.responseData) {
      return res.status(200).json({
        translatedText: data.responseData.translatedText,
        detectedLanguage: data.responseData.detectedLanguage || sourceLang,
      });
    }

    return res.status(502).json({ error: 'Translation failed', message: data.responseDetails || 'Unknown error' });
  } catch (error) {
    return res.status(500).json({ error: 'Translation failed', message: error.message });
  }
}
