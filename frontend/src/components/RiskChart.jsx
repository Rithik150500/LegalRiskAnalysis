import { useEffect, useRef } from 'react';
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
} from 'chart.js';
import { Bar, Doughnut } from 'react-chartjs-2';

ChartJS.register(
  CategoryScale,
  LinearScale,
  BarElement,
  ArcElement,
  Title,
  Tooltip,
  Legend
);

function RiskChart({ type, data }) {
  if (!data || Object.keys(data).length === 0) {
    return (
      <div className="flex items-center justify-center h-48 text-gray-400">
        No data available
      </div>
    );
  }

  const severityColors = {
    Critical: '#dc2626',
    High: '#f97316',
    Medium: '#eab308',
    Low: '#22c55e'
  };

  const categoryColors = {
    Contractual: '#3b82f6',
    Regulatory: '#8b5cf6',
    Litigation: '#ec4899',
    IP: '#14b8a6',
    Operational: '#f59e0b'
  };

  const colors = type === 'severity' ? severityColors : categoryColors;

  const labels = Object.keys(data);
  const values = Object.values(data);

  const chartData = {
    labels,
    datasets: [
      {
        data: values,
        backgroundColor: labels.map(label => colors[label] || '#94a3b8'),
        borderWidth: 0,
      },
    ],
  };

  const options = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        position: type === 'severity' ? 'bottom' : 'right',
        labels: {
          usePointStyle: true,
          boxWidth: 8,
        },
      },
      tooltip: {
        callbacks: {
          label: (context) => {
            const total = values.reduce((a, b) => a + b, 0);
            const percentage = total > 0 ? ((context.raw / total) * 100).toFixed(1) : 0;
            return `${context.label}: ${context.raw} (${percentage}%)`;
          },
        },
      },
    },
  };

  if (type === 'severity') {
    return (
      <div className="h-64">
        <Bar
          data={chartData}
          options={{
            ...options,
            plugins: {
              ...options.plugins,
              legend: { display: false },
            },
            scales: {
              y: {
                beginAtZero: true,
                ticks: {
                  stepSize: 1,
                },
              },
            },
          }}
        />
      </div>
    );
  }

  return (
    <div className="h-64">
      <Doughnut data={chartData} options={options} />
    </div>
  );
}

export default RiskChart;
