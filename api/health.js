// Simple health check endpoint for Node.js runtime
export default function handler(req, res) {
  res.status(200).json({ 
    status: 'ok', 
    timestamp: new Date().toISOString(),
    service: 'DocQuery API'
  });
}