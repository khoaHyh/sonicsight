This document is a brainstorm 🧠⛈️ on system design and the systematic approach to implementing this project. Not to be confused with "ML architecture" which is sometimes used as a synonym to describe the template or structure of the **model**.

## TODOs

- frontend, backend, data layer, etc., what does this look like for an app like this?
  - my gut feeling is I can make this as simple as I want but what does a productionized web app using ML look like behind the scenes?
- use mermaid diagrams to communicate typical access pattern (really just one function)
  - also use to help illustrate concepts for others and myself

## Components

**Frontend**: FastHTML 🏎️! Since we're doing the course via fast.ai platform, I figured it was worth giving the Python web framework a try.
**Backend**: Hugging Face Spaces 🤗 + Gradio is hosting our backend. This combination provides:

- free 🤑 way to host the data pre-processing and inference logic backend. The Gradio template provides a API so we can use any frontend layer to communicate with it.
- its an easy, almost instant, way to test changes to the model

**Hosting**: Going to self-host coolify and use cloudflare tunnels to serve the website. Also going to run the web server as a daemonized service.

## Roadmap

### 1. Data Collection and Project Components ✅

- Decide on a data set. Going to pick 1 of:
  - UrbanSound8K
  - ESC-50
- Libraries for spectrogram generation:
  - PyTorch Audio (torchaudio)
  - Librosa
- Decide on spectrogram parameters (FFT size, window type, hop length)

### 2. Model Selection and Training: ✅

This section will be applying a lot of the content in lessons 1 & 2 of "Practical Deep Learning for Coders". Training & testing model on Kaggle.

- Starting with a pretrained CNN (convolutional neural network) that works well for image classification
  - fast.ai introduced me to ResNet so I'll start looking there
- Adapt model for spectrogram classification
- Fine-tune on spectrograms with appropriate labels
- Evaluate performance on validation set

### 3. Prototype Development ✅

I'll use Hugging Face spaces to do POC for myself and full stack deployment later. The goal here is to get a sense of how our app looks when it's all put together.

- Create a simple prototype to process a single audio file to a spectrogram
- Export model from Kaggle to use on Hugging Face
- Use the model and classify the spectrogram

### 4. Iterate on Prototype ✅

- Use the FastHTML web framework to create the frontend
- Processing pipeline:
  - audio processing (convert uploaded audio to the right format)
  - spectrogram generation
  - model inference
  - display results
- Error handling

### 6. Testing and Deployment (👷🏻‍♂️ in progress)

- Deploy to platform of my choice
