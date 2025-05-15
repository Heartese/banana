import React, { useRef, useState, useEffect } from "react";
import * as tf from "@tensorflow/tfjs";
import Webcam from "react-webcam";
import "./App.css";
import { nextFrame } from "@tensorflow/tfjs";
import {drawRect} from "./utilities"; 

function App() {
  const webcamRef = useRef(null);
  const canvasRef = useRef(null);

  // Main function
  const runCoco = async () => {
    // 3. TODO - Load network 
    const net = await tf.loadGraphModel('https://banana-ripeness.s3.us-east.cloud-object-storage.appdomain.cloud/model.json')
    
    // Loop and detect hands
    setInterval(() => {
      detect(net);
    }, 16.7);
  };
  
 const [recommendation, setRecommendation] = useState("");

  const detect = async (net) => {
    // Check data is available
    if (
      typeof webcamRef.current !== "undefined" &&
      webcamRef.current !== null &&
      webcamRef.current.video.readyState === 4
    ) {
      // Get Video Properties
      const video = webcamRef.current.video;
      const videoWidth = webcamRef.current.video.videoWidth;
      const videoHeight = webcamRef.current.video.videoHeight;

      // Set video width
      webcamRef.current.video.width = videoWidth;
      webcamRef.current.video.height = videoHeight;

      // Set canvas height and width
      canvasRef.current.width = videoWidth;
      canvasRef.current.height = videoHeight;

      // 4. TODO - Make Detections
      const img = tf.browser.fromPixels(video)
      const resized = tf.image.resizeBilinear(img, [640,480])
      const casted = resized.cast('int32')
      const expanded = casted.expandDims(0)
      const obj = await net.executeAsync(expanded)
      
      console.log(await obj[0].array())

      const boxes = await obj[6].array()
      const classes = await obj[4].array()
      const scores = await obj[0].array()
      
      // Draw mesh
      const ctx = canvasRef.current.getContext("2d");

      // 5. TODO - Update drawing utility
      // drawSomething(obj, ctx)  
      requestAnimationFrame(() => {
        const bananaBoxes = [];
        const bananaClasses = [];
        const bananaScores = [];
      
      for (let i = 0; i < scores[0].length; i++) {
        if (scores[0][i] > 0.6) {
          const detectedClass = classes[0][i];

          let label = "";
          if (detectedClass === 1) label = "Freshripe";
          else if (detectedClass === 2) label = "Freshunripe";
          else if (detectedClass === 3) label = "Overripe";
          else if (detectedClass === 4) label = "Ripe";
          else if (detectedClass === 5) label = "Rotten";
          else if (detectedClass === 6) label = "Unripe";

          let recommendationText = "";
          if (label === "Unripe") {
            recommendationText = "Recommendation: The banana is unripe. Let it sit at room temperature until it ripens.";
          } else if (label === "Ripe") {
            recommendationText = "Recommendation: The banana is ripe. Ideal for eating or smoothies.";
          } else if (label === "Overripe") {
            recommendationText = "Recommendation: The banana is overripe. Best used for banana bread or composting.";
          } else if (label === "Rotten") {
            recommendationText = "Recommendation: Decompose! Use it a fertilizer.";
          } else if (label === "Freshripe") {
            recommendationText = "Recommendation: The banana is fresh and ripe. Perfect for eating or using in fruit salads.";
          } else if (label === "Freshunripe") {
            recommendationText = "Recommendation: The banana is fresh but unripe. Store at room temperature and wait a few days for ripening.";
          }
            setRecommendation(recommendationText);

          bananaBoxes.push(boxes[0][i]);
          bananaClasses.push(classes[0][i]);
          bananaScores.push(scores[0][i]);
        }
      }

      
        drawRect(bananaBoxes, bananaClasses, bananaScores, 0.6, videoWidth, videoHeight, ctx);
      });
    
      

      tf.dispose(img)
      tf.dispose(resized)
      tf.dispose(casted)
      tf.dispose(expanded)
      tf.dispose(obj)

    }
  };

  useEffect(()=>{runCoco()},[]);

  return (
    <div className="App">
      <header className="App-header">
      <button
      onClick={() => {
        fetch("http://localhost:5000/logout", {
          method: "GET",
          credentials: "include", // needed for session cookies
        })
          .then(() => {
            // Redirect to login page
            window.location.href = "http://localhost:5000"; // or wherever your login page is
          })
          .catch((err) => {
            console.error("Logout failed:", err);
          });
      }}
      style={{
        position: 'absolute',
        top: '70px',
        right: '20px',
        zIndex: 10,
        padding: '10px 20px',
        backgroundColor: 'blue',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer'
      }}
    >
      Logout
</button>

<button
  onClick={() => {
    window.location.href = "http://localhost:4000";
  }}
   style={{
        position: 'absolute',
        top: '20px',
        right: '20px',
        zIndex: 10,
        padding: '10px 20px',
        backgroundColor: 'blue',
        color: 'white',
        border: 'none',
        borderRadius: '5px',
        cursor: 'pointer'
      }}
>
  Back to Home
</button>

        <Webcam
          ref={webcamRef}
          muted={true} 
          style={{
            position: "absolute",
            marginLeft: "auto",
            marginRight: "auto",
            left: 0,
            right: 0,
            textAlign: "center",
            zindex: 9,
            width: 640,
            height: 480,
          }}
        />

        <canvas
          ref={canvasRef}
          style={{
            position: "absolute",
            marginLeft: "auto",
            marginRight: "auto",
            left: 0,
            right: 0,
            textAlign: "center",
            zindex: 8,
            width: 640,
            height: 480,
          }}
        />
        <p style={{
          position: "absolute",
          bottom: "20px",
          left: "50%",
          transform: "translateX(-50%)",
          backgroundColor: "rgba(0, 0, 0, 0.6)",
          color: "white",
          padding: "10px 20px",
          borderRadius: "10px",
          fontSize: "18px",
          zIndex: 10
        }}>
          {recommendation}
        </p>

      </header>
    </div>
  );
}

export default App;
