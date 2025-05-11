import boto3

# Step 1: Set up AWS client for LLM and Image Generation
llm_client = boto3.client('bedrock', region_name='us-west-2')  # Assuming you're using Bedrock
image_gen_client = boto3.client('bedrock', region_name='us-west-2')  # Same for Image Gen

# Step 2: Define the function to generate text prompt from LLM
def generate_text_prompt(attractions):
    prompt = f"Given the following Disneyland attractions: {attractions}, generate a detailed description for an image that represents these attractions as a fantasy landscape."

    response = llm_client.invoke_model(
        ModelId="your-llm-model-id",
        Body=prompt.encode('utf-8'),
        ContentType="application/json"
    )
    
    # Extract the response text from LLM
    text_prompt = response['Body'].read().decode('utf-8')
    
    return text_prompt

# Step 3: Define the function to generate the image
def generate_image_from_prompt(text_prompt):
    response = image_gen_client.invoke_model(
        ModelId="your-image-gen-model-id",
        Body=text_prompt.encode('utf-8'),
        ContentType="application/json"
    )
    
    # Extract the image URL or binary data from the response
    image_data = response['Body'].read()
    
    return image_data

# Step 4: Create the pipeline to generate the image
def create_disneyland_image_pipeline(attractions):
    # Generate text prompt from LLM
    text_prompt = generate_text_prompt(attractions)
    
    # Generate image using the text prompt
    image = generate_image_from_prompt(text_prompt)
    
    return image

# Example Usage
attractions = ["Pirates of the Caribbean", "Space Mountain", "Haunted Mansion"]
image = create_disneyland_image_pipeline(attractions)

# Save or return image based on requirements
with open('disneyland_image.png', 'wb') as f:
    f.write(image)