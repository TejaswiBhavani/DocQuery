// Status endpoint for monitoring
export default function handler(req, res) {
  const { method } = req;
  
  if (method !== 'GET') {
    return res.status(405).json({ error: 'Method not allowed' });
  }
  
  res.status(200).json({
    status: 'operational',
    version: '1.0.0',
    runtime: 'node',
    timestamp: new Date().toISOString()
  });
}