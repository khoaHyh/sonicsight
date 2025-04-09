# SonicSight

Takes simple audio files, generates a spectrogram and uses an image classification model to identify the sound. Created this web application to display the model I trained, applying lessons 1 & 2 of the [fast.ai course](https://course.fast.ai). Currently, the model is trained to only recognized dog & cat sounds.

![Screenshot of Sonicsight web app](https://raw.githubusercontent.com/khoaHyh/portfolio-v3/refs/heads/main/public/sonicsight.png)

## Components

```mermaid
flowchart TB
    subgraph "Frontend Network"
        subgraph "Raspberry Pi"
            subgraph "Piku PaaS"
                FastHTML["FastHTML Frontend"]
                NGINX["NGINX Server"]
            end
        end
    end

    subgraph "Cloudflare"
        CloudflareTunnel["Cloudflare Tunnel"]
    end

    subgraph "Internet"
        User["Internet User"]
    end

    subgraph "Hugging Face"
        GradioAPI["Gradio API"]
        subgraph "Inference"
            AIModel["Trained Model"]
        end
    end

    subgraph "Kaggle"
        KaggleServers["Training Servers"]
    end

    %% Connections for normal operation
    User -->|"Access Website"| CloudflareTunnel
    CloudflareTunnel -->|"Secure Tunnel"| NGINX
    %% Connection removed as Piku is inside Raspberry Pi
    NGINX -->|"Serve"| FastHTML
    FastHTML -->|"API Calls"| GradioAPI
    GradioAPI -->|"Inference"| AIModel

    %% Training relationship
    KaggleServers -->|"Trained & Exported"| AIModel

    %% Styling
    classDef homeNet fill:#f9f9f9,stroke:#333,stroke-width:1px;
    classDef cloud fill:#f0f8ff,stroke:#333,stroke-width:1px;
    classDef platformService fill:#e6ffe6,stroke:#333,stroke-width:1px;

    class User,Internet cloud;
    class RaspPi,Piku,FastHTML,NGINX homeNet;
    class CloudflareTunnel,GradioAPI,AIModel,KaggleServers platformService;
```

### Frontend

- FastHTML: Python frontend application/framework
- Raspberry Pi: Acts as home server hosting the application
- Piku: A lightweight Platform-as-a-Service (PaaS) running on Raspberry Pi
- NGINX: Web server that handles HTTP requests and serves content

### Network & Connectivity

- Cloudflare Tunnels: Securely exposes server to the internet without opening firewall ports

### Backend & AI (Cloud)

- Hugging Face Space: Hosts ML model and backend server for inference
- Gradio Client API: Provides the interface between frontend and the model
- Kaggle: Where I initially trained the model before deployment
