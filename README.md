# Image-Steganography
Steganography with Channel Distribution and LFSR Encryption

This Python script implements an advanced steganography system that hides secret messages in images using RGB channel distribution, DNA encoding, and Linear Feedback Shift Register (LFSR) encryption. The secret data is embedded into the least significant bits (LSBs) of an image's pixels with a specific distribution: up to 50% in the Blue channel, 25% in the Red channel, and 25% in the Green channel.

Features





Data Conversion: Converts text to binary and back for embedding and extraction.



Channel Distribution: Distributes data across RGB channels (50% Blue, 25% Red, 25% Green) to optimize embedding capacity and reduce visual impact.



LFSR Encryption: Encrypts the binary data using an LFSR-based keystream for added security.



DNA Encoding/Decoding: Encodes binary data into a DNA sequence (A, C, G, T) for an additional layer of obfuscation.



Payload Length Header: Embeds a 32-bit header to indicate the length of the hidden data, ensuring accurate extraction.



Error Handling: Includes checks for image size, seed length, and delimiter presence.

Requirements





Python 3.x



Libraries:





numpy (for image array manipulation)



PIL (Pillow, for image processing)



Install dependencies:

pip install numpy Pillow

Usage





Prepare an Input Image: Use a high-resolution PNG or JPEG image (input.jpg in the example).



Configure the Script:





Set the input_image path to your input image.



Set the output_image path for the stego image (e.g., stego_image_v2.png).



Define the secret_message to hide.



Provide an lfsr_password (binary string, at least 2 bits long for the default taps [1, 2]).



Run the Script:

python steganography_v2.py

The script will:





Embed the secret message into the image.



Save the stego image to the specified output_image path.



Extract the message from the stego image and verify it matches the original.

Code Structure





Section 1: Helper Functions - Converts text to binary and vice versa.



Section 1.5: Channel Distribution - Allocates data across RGB channels (50% Blue, 25% Red, 25% Green).



Section 2: LFSR Module - Generates a pseudo-random keystream for encryption.



Section 3: DNA Encoding/Decoding - Encodes binary data into DNA sequences and decodes back.



Section 4: Core Steganography - Embeds and extracts data using LSB steganography with channel distribution.



Section 5: Main Execution - Configures and runs the embedding/extraction process.

Example

input_image = "input.jpg"
output_image = "stego_image_v2.png"
secret_message = "This is a top secret message!"
lfsr_password = "101101"

embed(image_path=input_image, secret_data=secret_message, output_path=output_image, lfsr_seed=lfsr_password)
extracted_msg = extract(image_path=output_image, lfsr_seed=lfsr_password)
print(f"Extracted: {extracted_msg}")

Notes





Image Capacity: Ensure the input image has enough pixels to hold the secret data. Each pixel can store 3 bits (1 per RGB channel).



LFSR Seed: The seed must be at least as long as the largest tap index (default: 2 bits).



Delimiter: The script appends $$END$$ to the secret message to mark its end during extraction.



Security: The LFSR provides basic encryption. For stronger security, consider more advanced encryption methods.



Image Format: Use lossless formats like PNG for the output to avoid data loss.

Limitations





The script assumes the input image is in RGB format.



Large messages require large images to avoid capacity errors.



Incorrect LFSR seeds during extraction will result in failure to find the delimiter.
