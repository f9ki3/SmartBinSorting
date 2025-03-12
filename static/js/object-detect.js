const MODEL_PATH = "./static/waste-sort/";

let model, webcam, maxPredictions;
let canSendData = true; // Flag to control sending interval

// Load the image model and setup the webcam
async function init() {
  const modelURL = MODEL_PATH + "model.json";
  const metadataURL = MODEL_PATH + "metadata.json";

  // Load the model and metadata
  model = await tmImage.load(modelURL, metadataURL);
  maxPredictions = model.getTotalClasses();

  // Setup webcam
  const flip = true; // whether to flip the webcam
  webcam = new tmImage.Webcam(500, 400, flip); // Initial size
  await webcam.setup(); // request access to the webcam
  await webcam.play();
  window.requestAnimationFrame(loop);

  // Append webcam to DOM
  document.getElementById("webcam-container").appendChild(webcam.canvas);

  // Apply styling to make the webcam responsive
  webcam.canvas.style.width = "100%"; // Full width
  webcam.canvas.style.height = "auto"; // Maintain aspect ratio
  webcam.canvas.style.border = "5px solid green"; // Green border
  webcam.canvas.style.borderRadius = "30px"; // Rounded corners
}

async function loop() {
  webcam.update(); // update the webcam frame
  await predict();
  window.requestAnimationFrame(loop);
}

// Run the webcam image through the image model
async function predict() {
  const prediction = await model.predict(webcam.canvas);

  // Find the highest probability prediction
  const topPrediction = prediction.reduce(
    (max, pred) => (pred.probability > max.probability ? pred : max),
    prediction[0]
  );
  let data1 = topPrediction.className;

  // Send data only if allowed, then disable sending for 5 seconds
  if (canSendData) {
    console.log(data1);
    sendData(data1);

    canSendData = false;
    setTimeout(() => {
      canSendData = true;
    }, 10000);
  }
}

init();
