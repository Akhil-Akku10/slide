import React, { useState } from 'react';
import Slide from './Slide';

const SlideViewer = ({ slideData }) => {
  const [currentSlideIndex, setCurrentSlideIndex] = useState(0);

  if (!slideData || !slideData.slides || slideData.slides.length === 0) {
    return <div className="no-slides">No slides to display</div>;
  }

  const currentSlide = slideData.slides[currentSlideIndex];
  const totalSlides = slideData.slides.length;

  const goToPrevSlide = () => {
    setCurrentSlideIndex(prev => (prev > 0 ? prev - 1 : prev));
  };

  const goToNextSlide = () => {
    setCurrentSlideIndex(prev => (prev < totalSlides - 1 ? prev + 1 : prev));
  };

  return (
    <div className="slide-viewer">
      <div className="slide-nav">
        <button onClick={goToPrevSlide} disabled={currentSlideIndex === 0}>
          Previous
        </button>
        <span>Slide {currentSlideIndex + 1} of {totalSlides}</span>
        <button onClick={goToNextSlide} disabled={currentSlideIndex === totalSlides - 1}>
          Next
        </button>
      </div>
      
      <div className="slide-container" style={{
        backgroundColor: slideData.template.color_scheme.background,
        color: slideData.template.color_scheme.primary,
        fontFamily: slideData.template.font
      }}>
        <Slide slide={currentSlide} />
      </div>
    </div>
  );
};

export default SlideViewer;