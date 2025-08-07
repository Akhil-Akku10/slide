// src/components/ChartDisplay.jsx
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend,
} from 'chart.js';
import { Line, Bar } from 'react-chartjs-2';

// Register ChartJS components
ChartJS.register(
  CategoryScale,
  LinearScale,
  PointElement,
  LineElement,
  BarElement,
  Title,
  Tooltip,
  Legend
);

export default function ChartDisplay({ chartData }) {
  if (!chartData) return null;

  const renderChart = () => {
    switch (chartData.type) {
      case 'line':
        return <Line data={chartData.data} options={chartData.options} />;
      case 'bar':
        return <Bar data={chartData.data} options={chartData.options} />;
      default:
        return null;
    }
  };

  return (
    <div style={{ width: '100%', height: '400px' }}>
      {renderChart()}
    </div>
  );
}