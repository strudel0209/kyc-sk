# KYC Agent System

A document processing and financial data extraction system built on Microsoft Semantic Kernel and Azure OpenAI, designed to automate Know Your Client (KYC) processes.

## Overview

The KYC Agent System is designed to automate the extraction and analysis of financial information from various document types. It uses a suite of specialized AI agents to identify clients, classify documents, extract financial data, and calculate metrics like net worth.

The system can process bank statements, financial assets, liabilities, and other financial documents, extracting structured data that can be used for financial analysis, compliance, and client onboarding.

## Features

- **Multilingual Document Processing**: Detects language and translates non-English documents
- **Client Identification**: Extracts client names, account numbers, and other identifying information
- **Document Classification**: Categorizes financial documents by type
- **Financial Data Extraction**: Identifies assets, liabilities, and income information
- **Currency Normalization**: Standardizes financial values across different currencies
- **Net Worth Calculation**: Computes client net worth based on extracted assets and liabilities
- **Azure Integration**: Optional Azure Blob Storage for document processing and Azure Functions support

## System Architecture

The system consists of these key components:

- **Core System (KYCAgentSystem)**: Orchestrates the overall document processing workflow
- **Specialized Agents**:
  - ClientIdentificationAgent: Extracts client information
  - DocumentClassificationAgent: Classifies document types
  - AssetIdentificationAgent: Identifies financial assets
  - LiabilityIdentificationAgent: Identifies financial liabilities
  - CurrencyNormalizationAgent: Standardizes currency values
  - MultilingualAgent: Handles language detection and translation
  - NetWorthCalculatorAgent: Calculates net worth
  - FinancialOverviewAgent: Extracts comprehensive financial overviews

## Installation

### Prerequisites

- Python 3.11+ recommended
- Azure OpenAI API access
- (Optional) Azure Blob Storage account
- (Optional) Azure Document Intelligence (formerly Form Recognizer)

### Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/kyc-sk.git
   cd kyc-sk
   ```

2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   # On Windows
   venv\Scripts\activate
   # On Linux/macOS
   source venv/bin/activate
   ```

3. Install the required packages:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a `.env` file in the project root with your Azure credentials:
   ```
   AZURE_OPENAI_ENDPOINT=your-endpoint-url
   AZURE_OPENAI_API_KEY=your-api-key
   AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment-name
   
   # Optional - for Blob Storage support
   BLOB_CONNECTION_STRING=your-blob-connection-string
   FR_ENDPOINT=your-document-intelligence-endpoint
   FR_KEY=your-document-intelligence-key
   ```

## Configuration

The system can be configured to run locally with in-memory storage or use Azure Blob Storage for document processing:

- **Local Mode**: Set `use_blob_storage=False` when initializing the KYCAgentSystem
- **Azure Mode**: Set `use_blob_storage=True` to utilize Azure Blob Storage and Document Intelligence

### Environment Variables

| Variable | Description | Required |
| --- | --- | --- |
| AZURE_OPENAI_ENDPOINT | Azure OpenAI API endpoint URL | Yes |
| AZURE_OPENAI_API_KEY | Azure OpenAI API key | Yes |
| AZURE_OPENAI_DEPLOYMENT_NAME | Azure OpenAI model deployment name | Yes |
| AZURE_OPENAI_API_VERSION | API version (default: 2023-05-15) | No |
| BLOB_CONNECTION_STRING | Azure Blob Storage connection string | For Azure mode only |
| FR_ENDPOINT | Azure Document Intelligence endpoint | For Azure mode only |
| FR_KEY | Azure Document Intelligence key | For Azure mode only |

## Usage

### Running Locally

You can run the system locally using the provided `main.py` script:

```bash
python main.py
```

This will:
1. Load environment variables
2. Initialize the KYC system
3. Process a sample bank statement
4. Output the extracted information as JSON

### Running with Azure Functions

The system can be deployed as an Azure Function that triggers when documents are uploaded to a Blob Storage container:

1. Deploy the functions folder to an Azure Function App
2. Configure the required environment variables in your Function App settings
3. Upload documents to the "kyc-documents" container
4. Processed results will be stored in the "kyc-results" container

### Code Example

```python
import asyncio
from kyc.system import KYCAgentSystem

async def process_document(document_content, document_name):
    # Initialize the system
    system = KYCAgentSystem(use_blob_storage=False)
    
    # Process the document
    result = await system.analyze_document(document_content, document_name)
    
    # Use the result
    print(result)
    return result

# Run with asyncio
document = "Bank Statement\nAccount Holder: Jane Doe\nBalance: $10,000"
asyncio.run(process_document(document, "statement.txt"))
```

## Extending the System

### Adding New Agent Types

1. Create a new agent class in the `kyc/agents/` directory
2. Inherit from `BaseAgent` and implement your custom functionality
3. Register the agent in `KYCAgentSystem._register_agents()`

### Customizing Prompts

Each agent defines its own prompts in the respective agent class. Modify these prompts to customize how agents extract information from documents.

## Development

### Project Structure

```
kyc-sk/
├── kyc/                        # Main package
│   ├── agents/                 # Specialized agents
│   │   ├── asset_agent.py
│   │   ├── client_agent.py
│   │   └── ...
│   ├── storage/                # Storage implementations
│   │   ├── blob_storage.py
│   │   └── memory_store.py
│   ├── config.py               # Configuration settings
│   ├── system.py               # Main system implementation
│   └── utils.py                # Utility functions
├── functions/                  # Azure Functions
│   └── document_processor/     # Document processing function
├── main.py                     # Local execution script
├── run_test.py                 # Test script
├── requirements.txt            # Dependencies
└── .env                        # Environment variables
```

## License

[Specify your license here]

## Contributing

[Add contributing guidelines if applicable]