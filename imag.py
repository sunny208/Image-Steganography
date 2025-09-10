# steganography_v2.py

import numpy as np
from PIL import Image
import math # Import math for floor function

# ==============================================================================
# SECTION 1: HELPER FUNCTIONS FOR DATA CONVERSION (No Changes)
# ==============================================================================

def text_to_binary(text):
    """Converts a string of text into a binary string."""
    return ''.join(format(ord(char), '08b') for char in text)

def binary_to_text(binary):
    """Converts a binary string back into a human-readable string."""
    chars = [binary[i:i+8] for i in range(0, len(binary), 8)]
    text = ""
    for char_bin in chars:
        text += chr(int(char_bin, 2))
    return text

# ==============================================================================
# SECTION 1.5: NEW - CHANNEL DATA DISTRIBUTION LOGIC
# Description: Defines how the data bits are split among the R, G, B channels.
# ==============================================================================

def get_channel_distribution(total_len):
    """
    Calculates how many bits to allocate to each channel based on the rule:
    - Blue: <= 50%
    - Red: <= 25%
    - Green: <= 25% (takes the remainder)
    """
    blue_len = math.floor(total_len * 0.50)
    red_len = math.floor(total_len * 0.25)
    green_len = total_len - blue_len - red_len
    return blue_len, red_len, green_len

# ==============================================================================
# SECTION 2: LFSR MODULE (No Changes)
# ==============================================================================

def lfsr(seed, taps, length):
    """Generates a pseudo-random bitstream using an LFSR."""
    register = list(seed)
    tap_indices = [len(register) - t for t in taps]
    keystream = []
    for _ in range(length):
        output_bit = register[-1]
        keystream.append(output_bit)
        feedback_bit = 0
        for i in tap_indices:
            feedback_bit ^= int(register[i])
        register = [str(feedback_bit)] + register[:-1]
    return ''.join(keystream)

# ==============================================================================
# SECTION 3: DNA ENCODING / DECODING MODULE (No Changes)
# ==============================================================================

DNA_MAP = {"00": "A", "01": "C", "10": "G", "11": "T"}
DNA_MAP_REVERSE = {v: k for k, v in DNA_MAP.items()}

def dna_encode(binary_data):
    """Encodes a binary string into a DNA sequence."""
    if len(binary_data) % 2 != 0:
        binary_data += '0'
    dna_string = ""
    for i in range(0, len(binary_data), 2):
        dna_string += DNA_MAP[binary_data[i:i+2]]
    return dna_string

def dna_decode(dna_string):
    """Decodes a DNA sequence back into a binary string."""
    binary_data = ""
    for base in dna_string:
        binary_data += DNA_MAP_REVERSE[base]
    return binary_data

# ==============================================================================
# SECTION 4: CORE STEGANOGRAPHY FUNCTIONS (UPDATED)
# ==============================================================================

def embed(image_path, secret_data, output_path, lfsr_seed):
    """
    Embeds a secret message into an image file using channel distribution.
    """
    print("🚀 Starting embedding process...")
    
    # 1. Load the image
    try:
        image = Image.open(image_path, 'r').convert('RGB')
        img_array = np.array(image)
        height, width, _ = img_array.shape
        pixel_count = height * width
        print(f"✅ Image loaded: {width}x{height}, capacity per channel: {pixel_count} bits.")
    except FileNotFoundError:
        print(f"❌ Error: Image file not found at '{image_path}'")
        return

    # 2. Prepare, encrypt, and DNA-process the secret data
    delimiter = "$$END$$"
    data_to_hide = secret_data + delimiter
    binary_data = text_to_binary(data_to_hide)
    
    lfsr_taps = [1, 2]
    if len(lfsr_seed) < max(lfsr_taps):
        print(f"❌ Error: LFSR seed must be at least {max(lfsr_taps)} bits long.")
        return
    lfsr_keystream = lfsr(lfsr_seed, lfsr_taps, len(binary_data))
    encrypted_binary = ''.join(str(int(b1) ^ int(b2)) for b1, b2 in zip(binary_data, lfsr_keystream))
    
    dna_encoded = dna_encode(encrypted_binary)
    final_payload = dna_decode(dna_encoded)
    
    # 3. NEW: Prepend payload length as a 32-bit header
    payload_len = len(final_payload)
    len_header = format(payload_len, '032b')
    data_to_embed = len_header + final_payload
    total_len = len(data_to_embed)
    print(f"🔑 Payload prepared. Total bits to embed (header + data): {total_len}")

    # 4. NEW: Distribute data across channels
    blue_len, red_len, green_len = get_channel_distribution(total_len)
    
    # Check if each channel has enough capacity
    if blue_len > pixel_count or red_len > pixel_count or green_len > pixel_count:
        print("❌ Error: Secret data is too large to fit in the image with this distribution.")
        return
    
    print(f"📊 Distributing data: {blue_len} bits to Blue, {red_len} to Red, {green_len} to Green.")
    blue_data = data_to_embed[:blue_len]
    red_data = data_to_embed[blue_len : blue_len + red_len]
    green_data = data_to_embed[blue_len + red_len:]

    # 5. NEW: Embed data into the respective channels
    new_img_array = img_array.copy()
    blue_idx, red_idx, green_idx = 0, 0, 0
    
    for y in range(height):
        for x in range(width):
            # Get original pixel [R, G, B]
            pixel = new_img_array[y, x]
            
            # Embed in Red channel if there's data left for it
            if red_idx < len(red_data):
                r_bin = format(pixel[0], '08b')
                pixel[0] = int(r_bin[:-1] + red_data[red_idx], 2)
                red_idx += 1
                
            # Embed in Green channel
            if green_idx < len(green_data):
                g_bin = format(pixel[1], '08b')
                pixel[1] = int(g_bin[:-1] + green_data[green_idx], 2)
                green_idx += 1
                
            # Embed in Blue channel
            if blue_idx < len(blue_data):
                b_bin = format(pixel[2], '08b')
                pixel[2] = int(b_bin[:-1] + blue_data[blue_idx], 2)
                blue_idx += 1

    # 6. Save the new image
    encoded_image = Image.fromarray(new_img_array.astype('uint8'), 'RGB')
    encoded_image.save(output_path)
    print(f"🎉 Embedding complete! Stego image saved to '{output_path}'")

def extract(image_path, lfsr_seed):
    """
    Extracts a secret message from an image using channel distribution.
    """
    print("\n🔎 Starting extraction process...")
    
    try:
        image = Image.open(image_path, 'r')
        img_array = np.array(image)
    except FileNotFoundError:
        print(f"❌ Error: Image file not found at '{image_path}'")
        return

    # 1. NEW: Extract LSBs from each channel separately
    red_lsbs = ""
    green_lsbs = ""
    blue_lsbs = ""
    
    # R is channel 0, G is 1, B is 2
    for val in img_array[:, :, 0].flatten(): red_lsbs += format(val, '08b')[-1]
    for val in img_array[:, :, 1].flatten(): green_lsbs += format(val, '08b')[-1]
    for val in img_array[:, :, 2].flatten(): blue_lsbs += format(val, '08b')[-1]
    
    # 2. NEW: Reconstruct the 32-bit length header
    header_len = 32
    header_blue_len, header_red_len, header_green_len = get_channel_distribution(header_len)
    
    len_binary = blue_lsbs[:header_blue_len] + red_lsbs[:header_red_len] + green_lsbs[:header_green_len]
    if len(len_binary) != 32:
        print("❌ Error: Could not extract the full 32-bit header. Image may be too small or corrupted.")
        return
        
    payload_len = int(len_binary, 2)
    print(f"🔑 Header extracted. Expected payload length: {payload_len} bits.")

    # 3. NEW: Reconstruct the full encrypted payload based on the extracted length
    total_embedded_len = header_len + payload_len
    total_blue, total_red, total_green = get_channel_distribution(total_embedded_len)
    
    reconstructed_data = (
        blue_lsbs[:total_blue] + 
        red_lsbs[:total_red] + 
        green_lsbs[:total_green]
    )
    
    # Slice off the header to get the actual payload
    encrypted_payload = reconstructed_data[header_len:]
    
    # 4. Decrypt the payload with LFSR
    lfsr_taps = [1, 2]
    keystream = lfsr(lfsr_seed, lfsr_taps, len(encrypted_payload))
    decrypted_binary = ''.join(str(int(b1) ^ int(b2)) for b1, b2 in zip(encrypted_payload, keystream))
    
    # 5. Find the delimiter and convert to text
    delimiter = "$$END$$"
    binary_delimiter = text_to_binary(delimiter)
    delimiter_pos = decrypted_binary.find(binary_delimiter)
    
    if delimiter_pos != -1:
        final_binary_message = decrypted_binary[:delimiter_pos]
        secret_message = binary_to_text(final_binary_message)
        print("🎉 Extraction complete! Secret message found.")
        return secret_message
    else:
        print("🤷‍♂️ Extraction failed: Delimiter not found. Check if the LFSR seed is correct.")
        return None

# ==============================================================================
# SECTION 5: MAIN EXECUTION BLOCK (No Changes)
# ==============================================================================
if _name_ == '_main_':
    # --- Configuration ---
    input_image = "input.jpg"
    output_image = "stego_image_v2.png"
    secret_message = "This is a top secret message hidden with Python and channel distribution!"
    lfsr_password = "101101" 

    # --- Run the Process ---
    embed(
        image_path=input_image, 
        secret_data=secret_message, 
        output_path=output_image,
        lfsr_seed=lfsr_password
    )
    
    extracted_msg = extract(
        image_path=output_image, 
        lfsr_seed=lfsr_password
    )
    
    if extracted_msg:
        print(f"\n📄 Successfully extracted message: '{extracted_msg}'")
        assert extracted_msg == secret_message
        print("✅ Verification successful: Extracted message matches the original.")