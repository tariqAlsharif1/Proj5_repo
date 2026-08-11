# Import necessary library for generating text embeddings using Hugging Face models
from sentence_transformers import SentenceTransformer

# Load a pre-trained embedding model optimized for semantic similarity tasks
model = SentenceTransformer('all-MiniLM-L6-v2')

def generate_embedding(text: str) -> list:
    """
    Generate a numerical vector (embedding) for a given text string.
    
    Args:
        text (str): The input text (e.g., skill name or course description).
        
    Returns:
        list: A list of floats representing the embedding vector.
    """
    # Encode the text into a dense vector and convert it to a standard Python list
    vector = model.encode(text)
    return vector.tolist()

if __name__ == "__main__":
    # Test the embedding function locally
    sample_text = "Python Programming and Machine Learning"
    vector_result = generate_embedding(sample_text)
    print(f"Generated Vector Sample (first 5 values): {vector_result[:5]}")
    print(f"Total Vector Dimensions: {len(vector_result)}")