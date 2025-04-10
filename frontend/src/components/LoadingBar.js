import React, { useState, useEffect } from 'react';
import './LoadingBar.css'; // Ensure you create this CSS file for styling

const LoadingBar = ({ isLoading }) => {
  const [progress, setProgress] = useState(0);

  useEffect(() => {
    if (isLoading) {
      const interval = setInterval(() => {
        setProgress((oldProgress) => {
          const newProgress = oldProgress + 10;
          if (newProgress === 100) {
            clearInterval(interval);
          }
          return newProgress;
        });
      }, 100); // Adjust time interval to match backend response time later
    } else {
      setProgress(0);
    }
  }, [isLoading]);

  return (
    <div className="loading-bar-container">
      <div className="loading-bar" style={{ width: `${progress}%` }}></div>
    </div>
  );
};

export default LoadingBar;