
// This page is for scrolling through the different pieces in correlation to the full image.

import { useState, useEffect } from 'react';
import { useParams } from 'react-router-dom';

export default function SecondPage() {
  const {sessionId} = useParams();
  const [loading, setLoading] = useState(true);
  const [images, setImages] = useState([]);
  const [currentImage, setCurrentImage] = useState(0);
  const [currentBox, setCurrentBox] = useState(0);
  const [fullImage, setFullImage] = useState(null);
  
  var totalImages = 20;
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

  // Fetch uploaded images from backend
  useEffect(() => {
    const fetchImages = async () => {
      try {
        const response = await fetch("http://localhost:8000/api/get-images-base64", 
          {
          method:"POST",
          body: JSON.stringify({session:sessionId}),
          headers: { "Content-Type": "application/json" }
        }
        );
        const full_image_response = await fetch("http://localhost:8000/api/images/latest-base64");
        const data = await response.json();
        const fullImageData = await full_image_response.json();
        setFullImage(fullImageData)
        const imageData = data.images
        setImages(imageData);
        setLoading(false)
      } catch (err) {
        console.error("Error fetching images:", err);
      }
    };
    fetchImages();
  }, [sessionId]);

  totalImages = images.length

  if (loading) {
    return (
      <div className="flex flex-col items-center justify-center min-h-screen bg-gray-50">
        <div className="w-12 h-12 border-4 border-blue-600 border-t-transparent rounded-full animate-spin"></div>
        <p className="mt-4 text-gray-600 text-lg">Loading images...</p>
      </div>
    );
  }

  if (images.length === 0) {
    return <div className="text-center mt-20 text-gray-600">No images found.</div>;
  }
  
  // NOTE: Should be named the other way around, am too lazy to change - DB
  const currentIndex = images[currentImage];

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
            <div className="relative w-[500px] h-[400px] flex items-center justify-center border rounded-lg shadow-md bg-white">
            <img
              src={currentIndex.data}
              alt={currentIndex.filename}
              className="max-h-[380px] max-w-[480px] object-contain rounded-lg"
            />
            </div>
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
            <div className="text-4xl mb-4">
              Completed Image
              <div className="flex items-center justify-center border rounded-lg shadow-md bg-white">
              <img
                src={fullImage.data}
                alt={fullImage.filename}
                className="max-h-[1000px] max-w-[800px] object-contain rounded-lg"
              />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}