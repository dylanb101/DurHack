
// This page is for scrolling through the different pieces in correlation to the full image.

import { useState } from 'react';

export default function SecondPage() {
  const [currentImage, setCurrentImage] = useState(0);
  const [currentBox, setCurrentBox] = useState(0);
  
  const totalImages = 20;
  const boxesPerImage = 6;

  const handlePrevious = () => {
    if (currentBox > 0) {
      setCurrentBox(currentBox - 1);
    } else if (currentImage > 0) {
      setCurrentImage(currentImage - 1);
      setCurrentBox(boxesPerImage - 1);
    }
  };

  const handleNext = () => {
    if (currentBox < boxesPerImage - 1) {
      setCurrentBox(currentBox + 1);
    } else if (currentImage < totalImages - 1) {
      setCurrentImage(currentImage + 1);
      setCurrentBox(0);
    }
  };

  const isAtStart = currentImage === 0 && currentBox === 0;
  const isAtEnd = currentImage === totalImages - 1 && currentBox === boxesPerImage - 1;

  return (
    <div className="relative w-full h-screen flex bg-gray-100">
      {/* Close button */}
      <button
        onClick={() => window.location.href = '/'}
        className="absolute top-4 right-4 z-10 w-10 h-10 bg-white rounded-full shadow-lg hover:bg-gray-100 transition-colors flex items-center justify-center text-2xl text-gray-700 font-light"
        aria-label="Close"
      >
        ×
      </button>

      {/* Left side - Navigation */}
      <div className="w-[35%] h-full bg-white shadow-lg p-8 flex flex-col justify-center items-center">
        <div className="mb-8 text-center">
          <div className="text-sm text-gray-600 space-y-2">
            <div>Image: <span className="font-semibold">{currentImage + 1} / {totalImages}</span></div>
            
            <div>Box: <span className="font-semibold">{currentBox + 1} / {boxesPerImage}</span></div>
          </div>
        </div>

        <div className="flex gap-4">
          <button
            onClick={handlePrevious}
            disabled={isAtStart}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-black rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            ← Previous
          </button>
          <button
            onClick={handleNext}
            disabled={isAtEnd}
            className="flex items-center gap-2 px-6 py-3 bg-blue-600 text-black rounded-lg hover:bg-blue-700 disabled:bg-gray-300 disabled:cursor-not-allowed transition-colors"
          >
            Next →
          </button>
        </div>
      </div>

      {/* Right side - Full image display */}
      <div className="w-[65%] h-full flex items-center justify-center p-8">
        <div className="w-full h-full bg-white rounded-lg shadow-lg flex items-center justify-center">
          <div className="text-center">
            <div className="text-6xl mb-4">🖼️</div>
            <p className="text-gray-600 text-lg">Full image spot</p>
          </div>
        </div>
      </div>
    </div>
  );
}