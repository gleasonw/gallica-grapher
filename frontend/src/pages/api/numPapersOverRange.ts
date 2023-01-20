export default function handler (req, res) {
  const { startDate, endDate } = req.query;
  res.status(200).json({ total: 0 });
}