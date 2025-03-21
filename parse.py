import os
from langchain_ollama import OllamaLLM
from langchain_core.prompts import ChatPromptTemplate
from logger_config import setup_logger

# Set up logger for this module
logger = setup_logger(__name__, os.path.join('logs', 'parser.log'))

template = (
    "You are tasked with extracting specific information from the following text content: {dom_content}. "
    "Please follow these instructions carefully: \n\n"
    "1. **Extract Information:** Only extract the information that directly matches the provided description: {parse_description}. "
    "2. **No Extra Content:** Do not include any additional text, comments, or explanations in your response. "
    "3. **Empty Response:** If no information matches the description, return an empty string ('')."
    "4. **Direct Data Only:** Your output should contain only the data that is explicitly requested, with no other text."
)

# Dictionary of available models
AVAILABLE_MODELS = {
    "llama2": "llama2:latest",
    "llama3.2": "llama3.2:latest",
    "gemma": "gemma:latest",
    "mistral": "mistral:latest",
    "phi3": "phi3:latest",
    "qwen2.5": "qwen2.5:latest",
    "deepseek": "deepseek-r1:14b",
}

# Default model to use
DEFAULT_MODEL = "llama3.2:latest"


def parse_with_ollama(dom_chunks, parse_description, model_name=None):
    """
    Parse DOM chunks using the specified Ollama model with error handling.
    
    Args:
        dom_chunks: List of DOM content chunks to parse
        parse_description: Description of what to extract
        model_name: Name of the model to use (must be in AVAILABLE_MODELS)
        
    Returns:
        Parsed results as a string
    """
    logger.info(f"Starting parsing with description: {parse_description}")
    
    # Select model based on input, defaulting to llama3.2 if not specified or invalid
    if model_name and model_name in AVAILABLE_MODELS:
        model_to_use = AVAILABLE_MODELS[model_name]
    else:
        if model_name:
            logger.warning(f"Model '{model_name}' not found, defaulting to {DEFAULT_MODEL}")
        model_to_use = DEFAULT_MODEL

    logger.info(f"Using model: {model_to_use}")

    # Initialize the model
    try:
        model = OllamaLLM(model=model_to_use)
    except Exception as e:
        logger.error(f"Failed to initialize Ollama model '{model_to_use}': {str(e)}")
        raise RuntimeError(f"Model initialization failed: {str(e)}")

    # Set up the chain
    prompt = ChatPromptTemplate.from_template(template)
    chain = prompt | model

    parsed_results = []
    failed_chunks = []

    for i, chunk in enumerate(dom_chunks, start=1):
        try:
            logger.info(f"Processing chunk {i}/{len(dom_chunks)}")
            response = chain.invoke(
                {"dom_content": chunk, "parse_description": parse_description}
            )
            parsed_results.append(response)
            logger.debug(f"Successfully processed chunk {i}")
        except Exception as e:
            logger.error(f"Failed to parse chunk {i}: {str(e)}")
            failed_chunks.append(i)
            # Add a placeholder for failed chunks
            parsed_results.append(f"[Error processing chunk {i}]")
            
    if failed_chunks:
        logger.warning(f"Failed to process chunks: {failed_chunks}")
    
    logger.info(f"Parsing completed. Processed {len(dom_chunks)} chunks with {len(failed_chunks)} failures")
    return "\n".join(parsed_results)
