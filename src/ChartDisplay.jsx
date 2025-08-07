import React from 'react';
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

const ChartDisplay = ({ chartData }) => {
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
    <div className="chart-container">
      {renderChart()}
    </div>
  );
};

export default ChartDisplay;