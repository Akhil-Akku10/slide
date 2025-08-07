import React from 'react';
import ChartDisplay from './ChartDisplay';

const Slide = ({ slide }) => {
  const renderSlideContent = () => {
    switch (slide.type) {
      case 'title':
        return (
          <div className="title-slide">
            <h1>{slide.title}</h1>
            {slide.subtitle && <h2>{slide.subtitle}</h2>}
          </div>
        );
      case 'text':
        return (
          <div className="text-slide">
            <h2>{slide.title}</h2>
            <ul>
              {slide.content.map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          </div>
        );
      case 'chart':
        return (
          <div className="chart-slide">
            <h2>{slide.title}</h2>
            <ChartDisplay chartData={slide.chart} />
          </div>
        );
      default:
        return null;
    }
  };

  return (
    <div className="slide">
      {renderSlideContent()}
    </div>
  );
};

export default Slide;